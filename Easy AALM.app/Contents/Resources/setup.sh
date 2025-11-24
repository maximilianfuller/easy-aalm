#!/bin/bash

echo "========================================"
echo "Easy AALM - Automatic Setup"
echo "========================================"
echo ""

# Function to install Python on Mac
install_python_mac() {
    echo "Installing Python via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install python3
}

# Function to install Wine on Mac
install_wine_mac() {
    echo "Installing Wine via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    brew install --cask wine-stable
}

# Function to download AALM
download_aalm() {
    echo "Downloading AALM from EPA..."
    AALM_URL="https://www.epa.gov/sites/default/files/2021-01/aalm_v3-1-1.zip"
    curl -L -o aalm.zip "$AALM_URL" 2>/dev/null || wget -O aalm.zip "$AALM_URL" 2>/dev/null

    if [ -f aalm.zip ]; then
        unzip -q aalm.zip -d aalm_download
        # Find AALM_64.exe and update path in app.py
        AALM_PATH=$(find aalm_download -name "AALM_64.exe" | head -1)
        if [ -n "$AALM_PATH" ]; then
            AALM_FULL_PATH="$(cd "$(dirname "$AALM_PATH")" && pwd)/$(basename "$AALM_PATH")"
            echo "Found AALM at: $AALM_FULL_PATH"
            # Auto-update path in app.py (will be implemented)
        fi
        rm aalm.zip
    fi
}

# Auto-install Python if missing
if ! command -v python3 &> /dev/null; then
    echo "Python 3 not found. Installing automatically..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        install_python_mac
    else
        echo "Please install Python 3.8+ manually: https://www.python.org/downloads/"
        exit 1
    fi
fi

echo "Python found: $(python3 --version)"
echo ""

# Auto-install Wine if missing (Mac only)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v wine &> /dev/null; then
        echo "Wine not found. Installing automatically..."
        install_wine_mac
    else
        echo "Wine found: $(wine --version)"
    fi
fi

echo ""
if [ ! -f "venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists, skipping creation..."
fi

echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are already installed
python -c "import streamlit" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo ""
    echo "Installing dependencies (first time only)..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
else
    echo "Dependencies already installed, skipping..."
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To run Easy AALM, double-click run.sh"
echo ""
