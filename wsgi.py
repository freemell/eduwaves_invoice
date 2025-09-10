#!/usr/bin/env python3
"""
WSGI entry point for EDUwaves Invoice Generator
This file is used by Gunicorn to run the Flask application
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app, print_routes

# This is the WSGI application object
application = app

# Print startup information when WSGI is loaded
print("🚀 EDUwaves Invoice Generator - WSGI Application Loading")
print("📋 Available routes:")
print_routes()

# Check if template file exists
template_path = os.path.join('templates', 'index.html')
if os.path.exists(template_path):
    print(f"✅ Template file found: {template_path}")
else:
    print(f"❌ Template file not found: {template_path}")

# Check if data files exist
data_files = ['books_database.json', 'unique_schools.csv']
for file in data_files:
    if os.path.exists(file):
        print(f"✅ Data file found: {file}")
    else:
        print(f"❌ Data file missing: {file}")

print("✅ WSGI Application Ready!")

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 Testing WSGI server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
