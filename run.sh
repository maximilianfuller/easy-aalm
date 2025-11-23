#!/bin/bash

echo "========================================"
echo "Easy AALM - Starting Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Running setup first..."
    echo ""
    ./setup.sh
    if [ $? -ne 0 ]; then
        echo ""
        echo "Setup failed. Please check the error messages above."
        exit 1
    fi
    echo ""
    echo "Setup complete! Now starting the application..."
    echo ""
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
