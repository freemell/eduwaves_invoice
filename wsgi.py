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
from app import app

# This is the WSGI application object
application = app

if __name__ == "__main__":
    # This allows running the WSGI file directly for testing
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
