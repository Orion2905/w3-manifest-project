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
    logger.info("Starting application initialization...")
    from app import create_app
    app = create_app()
    logger.info("✅ Application created successfully!")
    
    # Test database connection
    with app.app_context():
        try:
            from app import db
            # Try a simple database query
            db.session.execute("SELECT 1").fetchone()
            logger.info("✅ Database connection successful!")
        except Exception as db_error:
            logger.error(f"⚠️  Database connection failed: {db_error}")
            # Don't fail the entire app - it can still serve health checks
            
except Exception as e:
    logger.error(f"❌ Application initialization failed: {e}")
    import traceback
    traceback.print_exc()
    # Create a minimal fallback app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def fallback():
        return {'status': 'error', 'message': 'Application failed to initialize'}, 500

if __name__ == '__main__':
    if app:
        # Run the application
        app.run(
            debug=True,
            host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000))
        )
