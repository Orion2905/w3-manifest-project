#!/usr/bin/env python
"""
Run script for the W3 Manifest Management System
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create the Flask application instance for gunicorn
app = None

try:
    from app import create_app
    app = create_app()
    print("✅ App created successfully")
except Exception as e:
    print(f"❌ Failed to create app: {e}")
    import traceback
    traceback.print_exc()
    # Create a simple fallback app that just returns an error message
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return {'status': 'error', 'message': f'Application failed to initialize: {str(e)}'}, 500

if __name__ == '__main__':
    if app:
        # Run the application
        app.run(
            debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000))
        )
