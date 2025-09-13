#!/usr/bin/env python3
"""
Flask application entry point for W3 Manifest Management System.
"""

import os
from app import create_app

# Create application instance
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5001))
    
    print(f"Starting W3 Manifest Management System...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug mode: {debug}")
    print(f"Running on: http://{host}:{port}")
    print(f"API endpoints available at: http://{host}:{port}/api/")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
