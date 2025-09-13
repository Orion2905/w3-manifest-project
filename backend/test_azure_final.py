#!/usr/bin/env python3
"""
Direct Azure Connection Test
Test Azure SQL Server connection with various methods
"""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("🔍 Environment Variables:")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL', 'NOT FOUND')[:100]}...")

# Test 1: Direct pyodbc
print("\n🔌 Test 1: Direct pyodbc connection")
try:
    import pyodbc
    
    conn_str = """
    Driver={ODBC Driver 18 for SQL Server};
    Server=tcp:w3manifest-sqlserver-prod.database.windows.net,1433;
    Database=w3manifest-db;
    Uid=w3admin;
    Pwd=W3Manifest2024!;
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
    """
    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"✅ Direct pyodbc SUCCESS! Users: {count}")
    conn.close()
    
except Exception as e:
    print(f"❌ Direct pyodbc FAILED: {e}")

# Test 2: SQLAlchemy engine
print("\n🔌 Test 2: SQLAlchemy engine")
try:
    from sqlalchemy import create_engine, text
    
    url = "mssql+pyodbc://w3admin:W3Manifest2024!@w3manifest-sqlserver-prod.database.windows.net:1433/w3manifest-db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
    
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"✅ SQLAlchemy SUCCESS! Users: {count}")
        
except Exception as e:
    print(f"❌ SQLAlchemy FAILED: {e}")

# Test 3: Flask app
print("\n🔌 Test 3: Flask app with production config")
try:
    import sys
    sys.path.append('.')
    
    from app import create_app, db
    from app.models.user import User
    
    # Force production config
    os.environ['FLASK_ENV'] = 'production'
    
    app = create_app('production')
    with app.app_context():
        users = User.query.all()
        print(f"✅ Flask app SUCCESS! Users: {len(users)}")
        
        # Check database URL being used
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Database URL type: {'Azure' if 'mssql+pyodbc' in db_url else 'SQLite'}")
        
except Exception as e:
    print(f"❌ Flask app FAILED: {e}")

print("\n🎯 Summary:")
print("If Test 1 and 2 work but Test 3 fails, it's a Flask config issue.")
print("If all tests fail, it's a connection/credential issue.")
print("If all tests work, your Flask app should work in production mode!")
