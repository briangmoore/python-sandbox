# Virtual Environments with Miniforge
A summary of why venvs matter, how we set them up, and best practices.

---

## 1. Why Virtual Environments Matter

### ✔️ The Problem
You originally resisted venvs because:
- you wanted “one global Python”  
- you didn’t want multiple copies of packages  
- you preferred simplicity  

But global Python quickly becomes messy:
- conflicting package versions  
- broken dependencies  
- impossible reproducibility  
- different machines drifting apart  

### ✔️ The Solution
Virtual environments isolate:
- Python version  
- installed packages  
- dependency trees  
- project‑specific tooling  

This makes multi‑machine workflows (Ubuntu + MSYS2) predictable.

---

## 2. How We Set Up Python 3.13 and 3.14

### Create Python 3.13 env:
```
mamba create -n py313 python=3.13
conda activate py313
```

### Create Python 3.14 env:
```
mamba create -n py314 python=3.14
conda activate py314
```

### Verify:
```
python --version
```

Each environment has its own interpreter:
- `py313` → Python 3.13  
- `py314` → Python 3.14  

This lets you test code across versions without breaking anything.

---

## 3. Best Practices for Miniforge + Virtual Environments

### ✔️ **Do This**
- Create one environment per project or per Python version  
- Keep `base` clean (no project packages)  
- Use `mamba` for installs  
- Use `conda activate` / `conda deactivate`  
- Store environment notes in your repo (`docs/`)  

### ❌ **Not That**
- Don’t install packages into `base`  
- Don’t mix pip + conda unless necessary  
- Don’t reuse old environments across major Python versions  
- Don’t delete environments manually (always use conda remove)  

---

## 4. Why This Matters for Your Workflow

### Multi‑machine consistency
You’re working on:
- MSYS2/Windows  
- Ubuntu 24  

Virtual environments ensure:
- same Python version  
- same packages  
- same behavior  
- same reproducibility  

### Git + Miniforge + venvs = stable workflow
Your repo stays clean.  
Your environments stay isolated.  
Your machines stay in sync.

---

## 5. Quick Commands Cheat Sheet

### List environments:
```
conda env list
```

### Activate:
```
conda activate py313
```

### Install packages:
```
mamba install matplotlib
```

### Freeze environment:
```
pip list --format=freeze > requirements.txt
```

### Remove environment:
```
conda remove -n py313 --all
```

---
