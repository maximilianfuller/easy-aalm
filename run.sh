#!/bin/bash

echo "========================================"
echo "Easy AALM - Starting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run ./setup.sh first"
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Streamlit app..."
echo ""
echo "The app will open in your browser at:"
echo "http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
