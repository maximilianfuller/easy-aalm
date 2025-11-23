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

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting Streamlit app...
echo.
echo The app will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
