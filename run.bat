@echo off
echo ========================================
echo Easy AALM - Starting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo First-time setup: Creating virtual environment...
    echo.

    REM Check if Python is installed
    python --version >nul 2>&1
    if errorlevel 1 (
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

    REM Create virtual environment
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )

    echo Installing dependencies...
    echo This may take a minute...
    venv\Scripts\python.exe -m pip install streamlit pandas plotly
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )

    echo.
    echo Setup complete! Starting the application...
    echo.
)

echo Starting Streamlit app...
echo.
echo Browser will open at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

REM Open browser after a short delay
timeout /t 2 /nobreak >nul
start http://localhost:8501

REM Start Streamlit using the venv Python directly
venv\Scripts\python.exe -m streamlit run app.py
