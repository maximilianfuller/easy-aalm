@echo off
echo === Building Easy AALM for Windows ===

REM Create build venv if needed
if not exist ".build-venv" (
    echo Creating build environment...
    python -m venv .build-venv
)

call .build-venv\Scripts\activate.bat
pip install -q pyinstaller pywebview

echo Building app...
pyinstaller easy_aalm_windows.spec --clean --noconfirm

echo Creating bundled Python environment...
set BUNDLE_VENV=dist\EasyAALM\venv
if exist "%BUNDLE_VENV%" rmdir /s /q "%BUNDLE_VENV%"
python -m venv "%BUNDLE_VENV%"

echo Installing Streamlit in bundled environment...
"%BUNDLE_VENV%\Scripts\pip" install -q streamlit pandas plotly openpyxl

echo.
echo === Build complete ===
echo App: dist\EasyAALM\Easy AALM.exe
dir /s dist\EasyAALM | find "File(s)"
pause
