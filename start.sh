#!/bin/bash

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:."
export PORT=${PORT:-5000}

# Try different Python commands in order of preference
if command -v python3 &> /dev/null; then
    echo "Using python3 on port $PORT"
    python3 app.py
elif command -v python &> /dev/null; then
    echo "Using python on port $PORT"
    python app.py
else
    echo "Python not found. Please install Python 3.8 or higher."
    exit 1
fi
