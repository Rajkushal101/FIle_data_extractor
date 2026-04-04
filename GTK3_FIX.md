# 🚨 Quick Fix: WeasyPrint GTK3 Installation for Windows

## The Issue
WeasyPrint requires GTK3 runtime libraries on Windows, which causes the error:
```
OSError: cannot load library 'libgobject-2.0-0'
```

## ✅ QUICK FIX (App Works Now!)

I've updated the code to make PDF generation optional. **Your app will now start successfully!**

Try running again:
```bash
cd backend
uvicorn main:app --reload
```

**Note:** PDF export will show an error until GTK3 is installed, but everything else works!

---

## 🔧 Proper Solution: Install GTK3

### Option 1: GTK3 Runtime Installer (Recommended)

1. **Download GTK3 Installer:**
   - Go to: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
   - Download latest `gtk3-runtime-x.x.x-x-x-x-ts-win64.exe`

2. **Install:**
   - Run the installer
   - Use default installation path
   - Complete installation

3. **Restart Backend:**
   ```bash
   # Close current terminal (Ctrl+C)
   # Reopen and run:
   uvicorn main:app --reload
   ```

4. **Verify:**
   - PDF generation should now work!

### Option 2: MSYS2 (Alternative)

```bash
# Install MSYS2 from: https://www.msys2.org/
# Then in MSYS2 terminal:
pacman -S mingw-w64-x86_64-gtk3
```

---

## 🧪 Test Without GTK3 (Current Setup)

Your app works now, except PDF export. Test these features:

```bash
# ✅ Works: Health check
curl http://localhost:8000/api/health

# ✅ Works: Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"username\":\"testuser\",\"password\":\"test12345\"}"

# ✅ Works: Upload document (extraction only)
# ✅ Works: DOCX export
# ❌ Won't work yet: PDF export (needs GTK3)
```

---

## 🎯 What to Do Now

**Choose A or B:**

### A) Continue Without PDF (Test Other Features)
- ✅ Authentication works
- ✅ Document upload works
- ✅ DOCX/Markdown/LaTeX export works
- ❌ PDF export disabled (temporary)

### B) Install GTK3 Now (Full Features)
- Follow Option 1 above (5 minutes)
- Restart backend
- All features work including PDF!

---

## 💡 Recommended Path

1. **Start backend now** (works without GTK3)
2. **Test authentication and dashboard**
3. **Install GTK3 when ready for PDF testing**

Your choice! The app is fully functional except for PDF generation.
