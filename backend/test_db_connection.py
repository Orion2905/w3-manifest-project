#!/usr/bin/env python
"""
Quick test script to verify database connectivity
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pymssql

# Test direct connection
try:
    print("Testing direct database connection...")
    conn = pymssql.connect(
        server='w3manifest-sqlserver-prod.database.windows.net',
        user='w3admin',
        password='W3Manifest2024!',
        database='w3manifest-db',
        timeout=30,
        login_timeout=30
    )
    print("✅ Direct database connection successful!")
    
    # Test a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    print(f"✅ Simple query result: {result}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    sys.exit(1)

# Test SQLAlchemy connection
try:
    print("\nTesting SQLAlchemy connection...")
    from sqlalchemy import create_engine, text
    
    # Use the same connection string as the app
    engine = create_engine(
        "mssql+pymssql://w3admin:W3Manifest2024!@w3manifest-sqlserver-prod.database.windows.net:1433/w3manifest-db?charset=utf8",
        echo=False
    )
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"✅ SQLAlchemy connection successful: {row}")
        
except Exception as e:
    print(f"❌ SQLAlchemy connection failed: {e}")
    sys.exit(1)

# Test Flask app creation
try:
    print("\nTesting Flask app creation...")
    from app import create_app
    
    app = create_app()
    print("✅ Flask app creation successful!")
    
    # Test with app context
    with app.app_context():
        from app.extensions import db
        result = db.session.execute(text("SELECT 1 as test")).fetchone()
        print(f"✅ Database query through Flask app successful: {result}")
        
except Exception as e:
    print(f"❌ Flask app creation/database test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 All tests passed! The app should work correctly.")
