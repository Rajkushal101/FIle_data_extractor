@echo off
REM ============================================
REM File Data Extractor - Windows Setup Script
REM ============================================

echo.
echo ========================================
echo   FILE DATA EXTRACTOR - SETUP
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python found:
python --version

REM Check Python version (3.9+)
echo.
echo Checking Python version...
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.9 or higher is required!
    echo Your version:
    python --version
    pause
    exit /b 1
)

echo [OK] Python version is compatible
echo.

REM Navigate to backend directory
cd /d "%~dp0..\backend"

echo ========================================
echo   STEP 1: Creating Virtual Environment
echo ========================================
echo.

if exist "venv" (
    echo [INFO] Virtual environment already exists
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)

echo.
echo ========================================
echo   STEP 2: Activating Virtual Environment
echo ========================================
echo.

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    pause
    exit /b 1
)

echo [OK] Virtual environment activated

echo.
echo ========================================
echo   STEP 3: Upgrading pip
echo ========================================
echo.

python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] Failed to upgrade pip, continuing anyway...
)

echo.
echo ========================================
echo   STEP 4: Installing Dependencies
echo ========================================
echo.

echo Installing core dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies!
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo [OK] Core dependencies installed!

echo.
echo ========================================
echo   STEP 5: Installing Optional Dependencies
echo ========================================
echo.

echo Installing optional packages (psutil, slowapi)...
pip install psutil slowapi
if errorlevel 1 (
    echo [WARNING] Optional dependencies failed, but core app will work
)

echo.
echo ========================================
echo   STEP 6: Creating Required Directories
echo ========================================
echo.

if not exist "uploads" mkdir uploads
if not exist "temp" mkdir temp

echo [OK] Directories created

echo.
echo ========================================
echo   STEP 7: Checking API Keys
echo ========================================
echo.

if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Creating .env from template...
    copy .env.example .env >nul 2>&1
    echo [ACTION REQUIRED] Please edit .env and add your API keys:
    echo   - GROQ_API_KEY
    echo   - GEMINI_API_KEY
) else (
    echo [OK] .env file exists
    echo.
    echo Checking API keys...
    python -c "from config import settings; print('[OK] GROQ_API_KEY:', 'SET' if settings.GROQ_API_KEY else 'MISSING'); print('[OK] GEMINI_API_KEY:', 'SET' if settings.GEMINI_API_KEY else 'MISSING')"
)

echo.
echo ========================================
echo   STEP 8: Running Startup Test
echo ========================================
echo.

echo Testing server startup...
python test_startup.py
if errorlevel 1 (
    echo [WARNING] Startup test failed, but you can still try running the server
)

echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Backend setup is complete!
echo.
echo To start the backend server:
echo   1. cd backend
echo   2. venv\Scripts\activate
echo   3. uvicorn main:app --reload
echo.
echo Or simply run:
echo   cd backend ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo.
echo API will be available at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo   FRONTEND SETUP (Optional)
echo ========================================
echo.
echo To setup the frontend (in a new terminal):
echo   1. cd frontend
echo   2. npm install
echo   3. npm run dev
echo.
echo Frontend will be available at: http://localhost:3000
echo.
echo ========================================

pause
