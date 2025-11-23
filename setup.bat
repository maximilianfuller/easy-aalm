@echo off
echo ========================================
echo Easy AALM - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
) else (
    echo Virtual environment already exists, skipping creation...
)

REM Check if dependencies are already installed
venv\Scripts\python.exe -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing dependencies (first time only)...
    echo This may take a minute...
    venv\Scripts\python.exe -m pip install --upgrade pip
    venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Installation complete!
) else (
    echo.
    echo Dependencies already installed, skipping...
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Download AALM from EPA website if you haven't already
echo 2. Update the aalm_paths in app.py to point to your AALM_64.exe
echo 3. Run the app using run.bat
echo.
pause
