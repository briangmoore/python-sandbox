#!/usr/bin/env python3
"""
cve_lookup.py — Quarterly vulnerability lookup against the NVD API v2.0

Queries the National Vulnerability Database for CVEs matching one or more
products/keywords (or CPE strings), and writes the results to CSV/JSON.

Usage examples
--------------
# Simple keyword search, all-time (matches the NVD website's default), to CSV
python cve_lookup.py --keywords "Femap" "Simcenter" "SolidWorks" --out results.csv

# Same, but restricted to the last 100 days (for quarterly incremental runs)
python cve_lookup.py --keywords "Femap" "Simcenter" "SolidWorks" --days 100 --out results.csv

# Use a config file listing products (one per line, "#" for comments)
python cve_lookup.py --keywords-file products.txt --days 90 --out results.csv

# Precise search using CPE strings instead of free-text keywords
python cve_lookup.py --cpe "cpe:2.3:a:siemens:femap" --days 365 --out results.json --format json

# Use an NVD API key (recommended — raises rate limit from 5 to 50 req/30s)
python cve_lookup.py --keywords "Femap" --api-key YOUR_KEY_HERE

Notes
-----
- Free-text keyword search can be noisy (NVD matches against the whole CVE
  description, not just a product-name field). Review results for false
  positives, or switch to --cpe for a specific vendor/product once you know
  the right CPE string (look it up at https://nvd.nist.gov/products/cpe/search).
- Without an API key NVD limits you to 5 requests per rolling 30s window.
  This script throttles automatically; a key just makes it faster (50/30s).
  Request a free key at: https://nvd.nist.gov/developers/request-an-api-key
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timedelta, timezone

import urllib.request
import urllib.parse
import urllib.error

NVD_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
RESULTS_PER_PAGE = 200  # NVD max per page


def throttle(api_key, last_call_time):
    """Sleep just enough to respect NVD rate limits."""
    min_interval = 30.0 / 50.0 if api_key else 30.0 / 5.0
    elapsed = time.monotonic() - last_call_time
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    return time.monotonic()


def build_query_params(keyword=None, cpe_name=None, start_date=None, end_date=None,
                        start_index=0):
    params = {
        "resultsPerPage": RESULTS_PER_PAGE,
        "startIndex": start_index,
    }
    if keyword:
        params["keywordSearch"] = keyword
        params["keywordExactMatch"] = ""  # presence-only flag; omit for substring match
        del params["keywordExactMatch"]
    if cpe_name:
        params["cpeName"] = cpe_name
    if start_date and end_date:
        # NVD requires ISO 8601 with milliseconds, e.g. 2024-01-01T00:00:00.000
        params["pubStartDate"] = start_date
        params["pubEndDate"] = end_date
    return params


def fetch_cves_for_term(term, is_cpe, days, api_key, verbose=False, end_days_ago=0):
    """Fetch all CVE pages for a single keyword or CPE string."""
    results = []
    start_index = 0
    total_results = None
    last_call = 0.0

    start_date = end_date = None
    if days is not None or end_days_ago:
        effective_days = days if days is not None else 3650
        end_dt = datetime.now(timezone.utc) - timedelta(days=end_days_ago)
        start_dt = end_dt - timedelta(days=effective_days)
        start_date = start_dt.strftime("%Y-%m-%dT%H:%M:%S.000")
        end_date = end_dt.strftime("%Y-%m-%dT%H:%M:%S.000")

    while total_results is None or start_index < total_results:
        params = build_query_params(
            keyword=None if is_cpe else term,
            cpe_name=term if is_cpe else None,
            start_date=start_date,
            end_date=end_date,
            start_index=start_index,
        )
        url = f"{NVD_BASE_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url)
        if api_key:
            req.add_header("apiKey", api_key)

        last_call = throttle(api_key, last_call)

        if verbose:
            print(f"  -> fetching '{term}' (startIndex={start_index})...", file=sys.stderr)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"  ! HTTP error for '{term}': {e.code} {e.reason}\n    {body[:300]}",
                  file=sys.stderr)
            break
        except urllib.error.URLError as e:
            print(f"  ! Network error for '{term}': {e.reason}", file=sys.stderr)
            break

        total_results = data.get("totalResults", 0)
        vulns = data.get("vulnerabilities", [])
        for v in vulns:
            cve = v.get("cve", {})
            results.append(parse_cve(cve, term))

        start_index += RESULTS_PER_PAGE
        if not vulns:
            break

    return results


def parse_cve(cve, search_term):
    cve_id = cve.get("id", "")
    published = cve.get("published", "")
    last_modified = cve.get("lastModified", "")

    descriptions = cve.get("descriptions", [])
    description = next((d["value"] for d in descriptions if d.get("lang") == "en"), "")

    metrics = cve.get("metrics", {})
    cvss_score, cvss_severity, cvss_vector = "", "", ""
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if key in metrics and metrics[key]:
            m = metrics[key][0]
            cvss_data = m.get("cvssData", {})
            cvss_score = cvss_data.get("baseScore", "")
            cvss_severity = m.get("baseSeverity", cvss_data.get("baseSeverity", ""))
            cvss_vector = cvss_data.get("vectorString", "")
            break

    weaknesses = cve.get("weaknesses", [])
    cwe_ids = []
    for w in weaknesses:
        for d in w.get("description", []):
            if d.get("lang") == "en":
                cwe_ids.append(d["value"])
    cwe_str = "; ".join(sorted(set(cwe_ids)))

    refs = cve.get("references", [])
    ref_urls = "; ".join(r.get("url", "") for r in refs[:5])

    return {
        "search_term": search_term,
        "cve_id": cve_id,
        "published": published,
        "last_modified": last_modified,
        "cvss_score": cvss_score,
        "cvss_severity": cvss_severity,
        "cvss_vector": cvss_vector,
        "cwe": cwe_str,
        "description": description,
        "references": ref_urls,
        "nvd_link": f"https://nvd.nist.gov/vuln/detail/{cve_id}" if cve_id else "",
    }


def load_keywords_file(path):
    terms = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    return terms


def write_csv(rows, path):
    fieldnames = [
        "search_term", "cve_id", "published", "last_modified",
        "cvss_score", "cvss_severity", "cwe", "description",
        "cvss_vector", "references", "nvd_link",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Quarterly CVE lookup against the NVD API v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--keywords", nargs="+", help="One or more free-text product names/keywords")
    src.add_argument("--keywords-file", help="Path to a text file, one keyword/product per line")
    src.add_argument("--cpe", nargs="+", help="One or more CPE strings (precise product match)")

    parser.add_argument("--days", type=int, default=None,
                        help="Restrict to CVEs published in a window this many days wide (NVD date-range search caps at ~120 days per request). "
                             "Default: no date restriction at all, matching the NVD website's default keyword search (all-time).")
    parser.add_argument("--end-days-ago", type=int, default=0,
                        help="Shift the whole search window back so it ends N days ago instead of today — "
                             "simulates 'what would this search have returned N days ago'. Useful for testing "
                             "the diff script without waiting for real new CVEs. Requires --days (defaults to "
                             "3650 if you set --end-days-ago without --days).")
    parser.add_argument("--out", default="cve_results.csv", help="Output file path")
    parser.add_argument("--format", choices=["csv", "json"], default=None,
                        help="Output format (inferred from --out extension if omitted)")
    parser.add_argument("--api-key", default=None, help="NVD API key (optional, raises rate limit)")
    parser.add_argument("--min-cvss", type=float, default=None,
                        help="Only keep results with CVSS base score >= this value")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")

    args = parser.parse_args()

    if args.days is not None and args.days > 120:
        print("Note: NVD's date-range search rejects windows longer than 120 days. "
              "Consider running quarterly with --days 100 or less, or splitting the range.",
              file=sys.stderr)
    if args.end_days_ago and args.days is None:
        print("Note: --end-days-ago without --days defaults to a 3650-day-wide window, which "
              "NVD's API will reject (max ~120 days). Pair it with --days, e.g. "
              "'--days 100 --end-days-ago 100'.", file=sys.stderr)

    if args.keywords:
        terms = [(k, False) for k in args.keywords]
    elif args.keywords_file:
        terms = [(k, False) for k in load_keywords_file(args.keywords_file)]
    else:
        terms = [(c, True) for c in args.cpe]

    all_rows = []
    for term, is_cpe in terms:
        print(f"Searching {'CPE' if is_cpe else 'keyword'}: {term}", file=sys.stderr)
        rows = fetch_cves_for_term(term, is_cpe, args.days, args.api_key, args.verbose,
                                    end_days_ago=args.end_days_ago)
        print(f"  -> {len(rows)} CVE(s) found", file=sys.stderr)
        all_rows.extend(rows)

    if args.min_cvss is not None:
        before = len(all_rows)
        all_rows = [
            r for r in all_rows
            if isinstance(r["cvss_score"], (int, float)) and r["cvss_score"] >= args.min_cvss
            or (isinstance(r["cvss_score"], str) and r["cvss_score"] and float(r["cvss_score"]) >= args.min_cvss)
        ]
        print(f"Filtered by min CVSS {args.min_cvss}: {before} -> {len(all_rows)}", file=sys.stderr)

    # de-duplicate by CVE ID while keeping the first search_term match note
    seen = {}
    for r in all_rows:
        if r["cve_id"] not in seen:
            seen[r["cve_id"]] = r
        else:
            seen[r["cve_id"]]["search_term"] += f", {r['search_term']}"
    deduped = list(seen.values())
    deduped.sort(key=lambda r: (r["cvss_score"] if isinstance(r["cvss_score"], (int, float)) else 0), reverse=True)

    fmt = args.format or ("json" if args.out.lower().endswith(".json") else "csv")
    if fmt == "json":
        write_json(deduped, args.out)
    else:
        write_csv(deduped, args.out)

    print(f"\nDone. {len(deduped)} unique CVE(s) written to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
