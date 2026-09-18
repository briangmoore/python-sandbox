#!/usr/bin/env python3
"""
cve_diff.py — Compare two cve_lookup.py output files and report what's new.

Meant to be run each quarter against this quarter's output and last
quarter's saved output, to surface only the CVEs you haven't already
triaged.

Usage
-----
python cve_diff.py --old q2_results.csv --new q3_results.csv --out q3_new.csv

# Also flag entries whose CVSS score or last-modified date changed since last time
python cve_diff.py --old q2_results.csv --new q3_results.csv --out q3_changes.csv --include-modified

# JSON in, JSON out
python cve_diff.py --old q2_results.json --new q3_results.json --out q3_new.json

Input files are expected to have the columns/fields produced by cve_lookup.py
(cve_id, published, last_modified, cvss_score, cvss_severity, cwe,
description, cvss_vector, references, nvd_link, search_term). Matching is
done on cve_id.
"""

import argparse
import csv
import json
import sys

FIELDNAMES = [
    "status", "search_term", "cve_id", "published", "last_modified",
    "cvss_score", "cvss_severity", "cwe", "description",
    "cvss_vector", "references", "nvd_link", "change_note",
]


def load_rows(path):
    """Load a cve_lookup.py output file (CSV or JSON) into a dict keyed by cve_id."""
    rows_by_id = {}
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for row in data:
            rows_by_id[row["cve_id"]] = row
    else:
        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows_by_id[row["cve_id"]] = row
    return rows_by_id


def diff(old_rows, new_rows, include_modified=False, include_removed=False):
    old_ids = set(old_rows.keys())
    new_ids = set(new_rows.keys())

    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    common_ids = old_ids & new_ids

    output = []

    for cid in added_ids:
        row = dict(new_rows[cid])
        row["status"] = "NEW"
        row["change_note"] = ""
        output.append(row)

    if include_modified:
        for cid in common_ids:
            old_r, new_r = old_rows[cid], new_rows[cid]
            changes = []
            for field in ("cvss_score", "cvss_severity", "last_modified"):
                old_val = str(old_r.get(field, ""))
                new_val = str(new_r.get(field, ""))
                if old_val != new_val:
                    changes.append(f"{field}: '{old_val}' -> '{new_val}'")
            if changes:
                row = dict(new_r)
                row["status"] = "MODIFIED"
                row["change_note"] = "; ".join(changes)
                output.append(row)

    if include_removed:
        for cid in removed_ids:
            row = dict(old_rows[cid])
            row["status"] = "REMOVED"
            row["change_note"] = "Present in old file, absent from new file (rare for CVE data)"
            output.append(row)

    def sort_key(r):
        try:
            score = float(r.get("cvss_score", 0) or 0)
        except ValueError:
            score = 0
        return score
    output.sort(key=sort_key, reverse=True)

    return output, added_ids, removed_ids, common_ids


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(rows, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Compare two cve_lookup.py output files and report new/changed CVEs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--old", required=True, help="Path to the older results file (CSV or JSON)")
    parser.add_argument("--new", required=True, help="Path to the newer results file (CSV or JSON)")
    parser.add_argument("--out", required=True, help="Path to write the diff report to")
    parser.add_argument("--format", choices=["csv", "json"], default=None,
                        help="Output format (inferred from --out extension if omitted)")
    parser.add_argument("--include-modified", action="store_true",
                        help="Also include CVEs present in both files whose CVSS score/severity "
                             "or last-modified date changed")
    parser.add_argument("--include-removed", action="store_true",
                        help="Also include CVEs present in the old file but missing from the new one "
                             "(rare — NVD doesn't usually delete entries, but reservations can be rejected/withdrawn)")

    args = parser.parse_args()

    old_rows = load_rows(args.old)
    new_rows = load_rows(args.new)

    output, added_ids, removed_ids, common_ids = diff(
        old_rows, new_rows,
        include_modified=args.include_modified,
        include_removed=args.include_removed,
    )

    fmt = args.format or ("json" if args.out.lower().endswith(".json") else "csv")
    if fmt == "json":
        write_json(output, args.out)
    else:
        write_csv(output, args.out)

    print(f"Old file: {len(old_rows)} CVE(s)", file=sys.stderr)
    print(f"New file: {len(new_rows)} CVE(s)", file=sys.stderr)
    print(f"New (not in old): {len(added_ids)}", file=sys.stderr)
    if args.include_removed:
        print(f"Removed (in old, not in new): {len(removed_ids)}", file=sys.stderr)
    print(f"Report written to {args.out} ({len(output)} row(s))", file=sys.stderr)


if __name__ == "__main__":
    main()
