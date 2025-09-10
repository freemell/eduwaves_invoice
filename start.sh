#!/bin/bash

# Try different Python commands in order of preference
if command -v python3 &> /dev/null; then
    echo "Using python3"
    python3 app.py
elif command -v python &> /dev/null; then
    echo "Using python"
    python app.py
else
    echo "Python not found. Please install Python 3.8 or higher."
    exit 1
fi
