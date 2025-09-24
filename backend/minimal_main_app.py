#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Minimal version of main Flask app to test imports and initialization
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_minimal_app():
    """Create minimal Flask app with basic configuration"""
    app = Flask(__name__)
    
    # Basic configuration with environment variables
    database_url = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not database_url:
        return None, "Missing SQLALCHEMY_DATABASE_URI environment variable"
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Initialize SQLAlchemy
    db = SQLAlchemy()
    db.init_app(app)
    
    @app.route('/')
    def root():
        return {
            'message': 'Minimal W3 Manifest API',
            'status': 'active',
            'database': 'connected'
        }, 200
    
    @app.route('/test-import')
    def test_import():
        try:
            # Test importing key modules
            from config import config
            from app.models import user
            return {
                'status': 'success',
                'message': 'All imports working',
                'config_loaded': True,
                'models_loaded': True
            }, 200
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Import error: {str(e)}',
                'error_type': type(e).__name__
            }, 500
    
    @app.route('/test-db')
    def test_db():
        try:
            with app.app_context():
                result = db.session.execute('SELECT 1 as test').fetchone()
                return {
                    'status': 'success',
                    'message': 'Database connection working',
                    'result': result[0] if result else None
                }, 200
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Database error: {str(e)}',
                'error_type': type(e).__name__
            }, 500
    
    return app, None

# For gunicorn
app, error = create_minimal_app()
if error:
    print(f"App creation failed: {error}")
    exit(1)

if __name__ == '__main__':
    if app:
        app.run(host='0.0.0.0', port=8000, debug=True)
    else:
        print(f"Failed to create app: {error}")
