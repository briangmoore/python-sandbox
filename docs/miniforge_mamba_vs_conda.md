# Miniforge: Mamba vs Conda + Correct Update Order
A practical “do this, not that” guide for using Miniforge efficiently.

---

## 1. Mamba vs Conda

### ✔️ **Do This**
Use **mamba** for:
- creating environments  
- installing packages  
- solving dependencies  
- updating environments  

Mamba is a drop‑in replacement for conda but dramatically faster because it uses a parallel dependency solver.

Example:
```
mamba create -n py313 python=3.13
mamba install numpy pandas
```

### ❌ **Not That**
Avoid using **conda** for heavy operations:
- slow dependency resolution  
- long environment creation times  
- occasional solver stalls  

Conda is still fine for:
```
conda activate myenv
conda deactivate
```

---

## 2. Correct Update Order After Installing Miniforge

### ✔️ **Do This (recommended sequence)**
After installing Miniforge:

```
mamba update --all
mamba update conda
mamba update python
```

This ensures:
- base environment is current  
- conda‑forge metadata is fresh  
- Python is updated safely  
- dependency solver stays consistent  

### ❌ **Not That**
Do **not** run:
```
conda update --all
```
This can:
- pull in Anaconda‑branded packages  
- cause channel priority conflicts  
- slow down updates  
- break Miniforge’s clean environment model  

---

## 3. Best Practices for Miniforge

### ✔️ **Do This**
- Keep base environment minimal  
- Use mamba for all installs  
- Create separate envs for each Python version  
- Prefer conda‑forge packages  

### ❌ **Not That**
- Don’t install random packages into `base`  
- Don’t mix pip and conda in the same environment unless necessary  
- Don’t use Anaconda Navigator (not compatible with Miniforge)  

---

## 4. Quick Commands Cheat Sheet

### Create env:
```
mamba create -n py314 python=3.14
```

### Activate:
```
conda activate py314
```

### Install packages:
```
mamba install requests
```

### Update env:
```
mamba update --all
```

### Remove env:
```
conda remove -n py314 --all
```

---
