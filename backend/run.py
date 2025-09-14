#!/usr/bin/env python
"""
Run script for the W3 Manifest Management System
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create the Flask application instance for gunicorn
app = create_app()

if __name__ == '__main__':
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
