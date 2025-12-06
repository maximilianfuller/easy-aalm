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

    # On macOS, check if Wine is installed (needed to run AALM Windows executable)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v wine &> /dev/null; then
            echo "Wine is not installed. Wine is required to run AALM on macOS."
            echo ""

            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                echo "Homebrew is not installed. Installing Homebrew first..."
                echo ""
                echo "Please follow the prompts to install Homebrew."
                echo "You may be asked for your password."
                echo ""

                # Install Homebrew
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

                if [ $? -ne 0 ]; then
                    echo ""
                    echo "ERROR: Failed to install Homebrew"
                    echo ""
                    echo "Please install Homebrew manually from https://brew.sh"
                    echo "Then run this app again."
                    echo ""
                    read -p "Press Enter to exit..."
                    exit 1
                fi

                # Add Homebrew to PATH for this session
                if [[ $(uname -m) == "arm64" ]]; then
                    eval "$(/opt/homebrew/bin/brew shellenv)"
                else
                    eval "$(/usr/local/bin/brew shellenv)"
                fi
            fi

            echo "Installing Wine..."
            echo "This may take several minutes..."
            echo ""

            # Install wine-crossover (works on both Intel and Apple Silicon)
            brew tap gcenx/wine
            brew install --cask wine-crossover

            if ! command -v wine &> /dev/null; then
                echo ""
                echo "ERROR: Failed to install Wine"
                echo ""
                echo "Please install Wine manually:"
                echo "  brew tap gcenx/wine"
                echo "  brew install --cask wine-crossover"
                echo ""
                echo "Then run this app again."
                echo ""
                read -p "Press Enter to exit..."
                exit 1
            fi

            echo ""
            echo "Wine installed successfully!"
            echo ""
        fi
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
    cp "$APP_RESOURCES/fortran_input_generator.py" "$USER_DATA_DIR/"

    echo ""
    echo "Setup complete! Starting the application..."
    echo ""
fi

# Always ensure AALM executables have execute permissions (every run)
if [ -f "$USER_DATA_DIR/aalm_original/AALM_64.exe" ]; then
    chmod +x "$USER_DATA_DIR/aalm_original/AALM_64.exe" 2>/dev/null || true
fi
if [ -f "$USER_DATA_DIR/aalm_original/AALM_32.exe" ]; then
    chmod +x "$USER_DATA_DIR/aalm_original/AALM_32.exe" 2>/dev/null || true
fi

# Always update app files from app bundle (in case we've updated them)
if [ -f "$APP_RESOURCES/app.py" ]; then
    cp "$APP_RESOURCES/app.py" "$USER_DATA_DIR/app.py" 2>/dev/null || true
fi
if [ -f "$APP_RESOURCES/fortran_input_generator.py" ]; then
    cp "$APP_RESOURCES/fortran_input_generator.py" "$USER_DATA_DIR/fortran_input_generator.py" 2>/dev/null || true
fi

# Always ensure required template files exist (copy missing ones from app bundle)
if [ -d "$APP_RESOURCES/aalm_original/Examples" ]; then
    mkdir -p "$USER_DATA_DIR/aalm_original/Examples"
    # Copy any missing template files
    for template in "$APP_RESOURCES/aalm_original/Examples"/*.txt; do
        if [ -f "$template" ]; then
            template_name=$(basename "$template")
            if [ ! -f "$USER_DATA_DIR/aalm_original/Examples/$template_name" ]; then
                cp "$template" "$USER_DATA_DIR/aalm_original/Examples/$template_name" 2>/dev/null || true
            fi
        fi
    done
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
