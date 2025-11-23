@echo off
echo ========================================
echo Easy AALM - Starting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Running setup first...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo.
        echo Setup failed. Please check the error messages above.
        pause
        exit /b 1
    )
    echo.
    echo Setup complete! Now starting the application...
    echo.
)

echo Starting Streamlit app...
echo.
echo Opening browser in 3 seconds...
echo.
echo Press Ctrl+C to stop the application
echo.

REM Open browser after a delay (in a separate process)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8501"

REM Start Streamlit using the venv Python directly
venv\Scripts\python.exe -m streamlit run app.py
