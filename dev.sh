#!/bin/bash
# Development script - runs streamlit directly from source

cd "$(dirname "$0")"

# Source Homebrew if available (needed for Wine on macOS)
if [ -f /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Check for venv, create if needed
if [ ! -f "venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    venv/bin/pip install streamlit pandas plotly openpyxl
fi

echo "Starting Streamlit (dev mode)..."
echo "http://localhost:8501"
echo ""

# Run from project root so paths work correctly
cd "$(dirname "$0")"
venv/bin/python -m streamlit run src/app.py --server.headless true
