# 🔧 Python Version Compatibility Issue

## Problem
PyMuPDF 1.23.21 doesn't have pre-built wheels for Python 3.14, causing build failures.

## ✅ Solutions (Choose ONE):

### Option 1: Use Python 3.11 or 3.12 (RECOMMENDED)
```bash
# Download Python 3.12 from:
https://www.python.org/downloads/release/python-3120/

# After installing Python 3.12:
1. Delete the venv folder: rmdir /s backend\venv
2. Run setup.bat again: scripts\setup.bat
```

### Option 2: Install Latest PyMuPDF (Try this first!)
```bash
cd backend
venv\Scripts\activate
pip install --upgrade pymupdf
pip install -r requirements.txt
```

### Option 3: Use Pre-built Binary
```bash
cd backend
venv\Scripts\activate
pip install pymupdf-binary
pip install -r requirements.txt
```

## Quick Test After Fix:
```bash
cd backend
venv\Scripts\activate
python -c "import fitz; print('PyMuPDF works!')"
```

## Why This Happens:
- Python 3.14 is very new (2026)
- PyMuPDF older versions don't have compiled wheels for it
- Installing from source requires Visual Studio C++ build tools
- Easier to use newer PyMuPDF or older Python

## Recommended Action:
**Use Python 3.12 (most stable with all packages)**
