#!/bin/bash

echo "========================================"
echo "Easy AALM - Mac/Linux Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    echo "  Mac: brew install python3"
    echo "  or download from python.org"
    exit 1
fi

echo "Python found: $(python3 --version)"
echo ""

# Check if Wine is installed (needed for running Windows AALM executable)
if ! command -v wine &> /dev/null; then
    echo "WARNING: Wine is not installed"
    echo "Wine is needed to run the Windows AALM executable on Mac/Linux"
    echo ""
    echo "To install Wine:"
    echo "  Mac: brew install --cask wine-stable"
    echo "  Ubuntu/Debian: sudo apt install wine"
    echo ""
    read -p "Continue without Wine? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "Wine found: $(wine --version)"
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Download AALM from EPA website if you haven't already"
echo "2. Update the aalm_paths in app.py to point to your AALM_64.exe"
echo "3. Run the app using ./run.sh"
echo ""
