#!/usr/bin/env python
"""
Minimal app with database connection test
"""
import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return {'status': 'success', 'message': 'Backend API is running!'}, 200

@app.route('/db-test')
def db_test():
    try:
        # Test database connection
        import pymssql
        
        conn = pymssql.connect(
            server='w3manifest-sqlserver-prod.database.windows.net',
            user='w3admin',
            password='W3Manifest2024!',
            database='w3manifest-db',
            timeout=30
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {'status': 'success', 'message': 'Database connection successful', 'result': result[0]}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': f'Database connection failed: {str(e)}'}, 500

@app.route('/sqlalchemy-test')
def sqlalchemy_test():
    try:
        # Test SQLAlchemy connection
        from sqlalchemy import create_engine, text
        
        db_uri = os.environ.get(
            'SQLALCHEMY_DATABASE_URI',
            'mssql+pymssql://w3admin:W3Manifest2024!@w3manifest-sqlserver-prod.database.windows.net:1433/w3manifest-db?charset=utf8'
        )
        
        engine = create_engine(db_uri, echo=False)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
        return {'status': 'success', 'message': 'SQLAlchemy connection successful', 'result': row[0]}, 200
        
    except Exception as e:
        return {'status': 'error', 'message': f'SQLAlchemy connection failed: {str(e)}'}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
