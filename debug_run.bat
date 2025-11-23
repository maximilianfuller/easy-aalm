@echo off
echo ========================================
echo Easy AALM - DEBUG MODE
echo ========================================
echo.

echo Current directory:
cd
echo.

echo Checking for venv...
if exist "venv\Scripts\activate.bat" (
    echo venv found!
) else (
    echo ERROR: venv not found!
    echo Running setup first...
    call setup.bat
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Checking Python in venv:
where python
python --version
echo.

echo Checking if streamlit is installed:
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"
if errorlevel 1 (
    echo ERROR: Streamlit not found!
    pause
    exit /b 1
)
echo.

echo Checking if app.py exists:
if exist "app.py" (
    echo app.py found!
) else (
    echo ERROR: app.py not found!
    pause
    exit /b 1
)
echo.

echo Starting Streamlit...
echo If this hangs, press Ctrl+C
echo.
streamlit run app.py

pause
