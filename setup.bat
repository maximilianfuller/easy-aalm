@echo off
echo ========================================
echo Easy AALM - Windows Setup
echo ========================================
echo.

REM Check if Python is installed
echo Checking for Python...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
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
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists, skipping creation...
)

echo.

REM Check if dependencies are already installed
venv\Scripts\python.exe -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies (first time only)...
    echo This may take a minute...
    venv\Scripts\python.exe -m pip install streamlit pandas plotly
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
    echo.
    echo Installation complete!
) else (
    echo Dependencies already installed, skipping...
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo Run the app using run.bat
echo.
pause
