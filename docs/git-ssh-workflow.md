# Git + SSH Multi‑Machine Workflow Guide
A practical reference for working with the same GitHub repo across multiple machines (MSYS2/Windows + Ubuntu Linux).

---

## 1. SSH Keys on Multiple Machines
Each machine needs its own SSH key added to GitHub.

### Check for an existing key
```
ls ~/.ssh
```

### If you already have a key
Add the public key to GitHub:
```
cat ~/.ssh/id_rsa.pub
```

Copy → GitHub → Settings → SSH and GPG keys → New SSH key.

### Test GitHub authentication
```
ssh -T git@github.com
```

---

## 2. Cloning the Repo on Each Machine
Use the SSH URL:
```
git clone git@github.com:briangmoore/python-sandbox.git
```

---

## 3. Understanding `origin` and `master`
`origin` = remote GitHub repo  
`master` = your local branch

First push:
```
git push --set-upstream origin master
```

---

## 4. Keeping Machines in Sync

### Step 1 — Fetch updates
```
git fetch
```

### Step 2 — Check status
```
git status
```

### If behind:
```
git pull
```

---

## 5. Seeing What Changed on GitHub

### Compare commit history
Remote:
```
git log origin/master --oneline
```

Local:
```
git log --oneline
```

### File‑level differences
```
git diff master..origin/master
```

---

## 6. Normal Daily Workflow

### Make changes
```
git add .
git commit -m "message"
git push
```

### Pull changes
```
git pull
```

---

## 7. Optional: Clone Into a Specific Folder
```
git clone git@github.com:briangmoore/python-sandbox.git myfolder
```

Or into current directory:
```
git clone git@github.com:briangmoore/python-sandbox.git .
```

---

## 8. Recommended Setup
- Pin this Copilot conversation  
- Save this Markdown file in your repo under `docs/`  
- Use SSH on all machines  

