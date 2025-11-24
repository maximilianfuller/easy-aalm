#!/bin/bash

# Get the directory where this script is located (app bundle Resources)
APP_RESOURCES="$(cd "$(dirname "$0")" && pwd)"

# Use user's Application Support directory for writable data
USER_DATA_DIR="$HOME/Library/Application Support/Easy AALM"
mkdir -p "$USER_DATA_DIR"

# Change to user data directory
cd "$USER_DATA_DIR"

echo "========================================"
echo "Easy AALM - Starting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "$USER_DATA_DIR/venv/bin/python" ]; then
    echo "First-time setup: Creating virtual environment..."
    echo ""

    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "ERROR: Python 3 is not installed"
        echo ""
        echo "Please install Python from:"
        echo "https://www.python.org/downloads/"
        echo ""
        echo "Or install via Homebrew:"
        echo "brew install python3"
        echo ""
        read -p "Press Enter to exit..."
        exit 1
    fi

    # Create virtual environment
    python3 -m venv "$USER_DATA_DIR/venv"
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "Installing dependencies..."
    echo "This may take a minute..."
    "$USER_DATA_DIR/venv/bin/python" -m pip install streamlit pandas plotly
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        read -p "Press Enter to exit..."
        exit 1
    fi

    echo "Copying app files to user directory..."
    cp -r "$APP_RESOURCES/aalm_original" "$USER_DATA_DIR/"
    cp -r "$APP_RESOURCES/.streamlit" "$USER_DATA_DIR/"
    cp "$APP_RESOURCES/app.py" "$USER_DATA_DIR/"

    echo ""
    echo "Setup complete! Starting the application..."
    echo ""
fi

echo "Starting Streamlit app..."
echo ""
echo "Browser will open at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Open browser after a short delay
sleep 2
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8501
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8501 2>/dev/null || true
fi &

# Start Streamlit using the venv Python, running from user data directory
cd "$USER_DATA_DIR"
"$USER_DATA_DIR/venv/bin/python" -m streamlit run "$USER_DATA_DIR/app.py" --server.headless true
