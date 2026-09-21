# Environment Setup Guide

This guide details how to configure a Python 3.11 virtual environment for the Credit Risk & Financial Inclusion ML project on Windows.

---

## Prerequisites & Installation Steps

### 1. Install Python 3.11 from python.org
Download and install Python 3.11 (e.g., Python 3.11.9) from [python.org](https://www.python.org/downloads/release/python-3119/).
> **Note:** During installation on Windows, ensure you check the box **"Add Python 3.11 to PATH"**.

---

### 2. Create venv: `py -3.11 -m venv .venv`
Open PowerShell or Command Prompt at the project root directory (`Syncrhony Assignement`) and run:

```bash
py -3.11 -m venv .venv
```

---

### 3. Activate on Windows: `.venv\Scripts\activate`
Activate the virtual environment:

**PowerShell:**
```powershell
.venv\Scripts\activate
```

**Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and reactivate).*

---

### 4. Install requirements: `pip install -r requirements.txt`
Ensure `pip` is up to date, then install the pinned dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 5. Verify: `python --version` should show `3.11.x`
Confirm that your virtual environment is active and running Python 3.11:

```bash
python --version
```

Expected output:
```text
Python 3.11.x
```

To also verify package availability:
```bash
python -c "import pandas, numpy, lightgbm, sklearn, shap, fastapi, chromadb; print('All core packages imported successfully!')"
```
