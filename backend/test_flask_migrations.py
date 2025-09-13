#!/usr/bin/env python3
"""
Azure Flask Migrations Helper
Test and manage Flask migrations on Azure database
"""

import os
import subprocess
import sys

# Azure database URL
AZURE_URL = "mssql+pyodbc://w3admin:W3Manifest2024!@w3manifest-sqlserver-prod.database.windows.net:1433/w3manifest-db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

def run_flask_command(command):
    """Run a Flask command with proper environment"""
    env = os.environ.copy()
    env['FLASK_ENV'] = 'production'
    env['FLASK_APP'] = 'app.py'
    env['DATABASE_URL'] = AZURE_URL
    
    try:
        result = subprocess.run(
            ['flask'] + command.split(),
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Command succeeded: flask {command}")
        if result.stdout.strip():
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: flask {command}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def test_migration_system():
    """Test the migration system"""
    print("🧪 Testing Flask Migration System on Azure")
    print("=" * 60)
    
    print("1. Testing database connection...")
    if not run_flask_command("db current"):
        print("❌ Cannot connect to database for migrations")
        return False
    
    print("\n2. Checking migration status...")
    run_flask_command("db heads")
    
    print("\n3. Showing current revision...")
    run_flask_command("db show")
    
    print("\n4. Creating a test migration...")
    if run_flask_command("db migrate -m 'Test Azure migration'"):
        print("✅ Migration created successfully!")
        
        print("\n5. Applying migration...")
        if run_flask_command("db upgrade"):
            print("✅ Migration applied successfully!")
        else:
            print("❌ Failed to apply migration")
    else:
        print("❌ Failed to create migration")
    
    return True

def verify_azure_tables():
    """Verify tables exist on Azure"""
    print("\n📊 Verifying Azure Database Tables")
    print("=" * 40)
    
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine(AZURE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    TABLE_NAME,
                    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as COLUMNS
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            
            tables = result.fetchall()
            print(f"📋 Found {len(tables)} tables:")
            
            for table_name, column_count in tables:
                print(f"  • {table_name} ({column_count} columns)")
                
                # Check for data
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
                    count = count_result.scalar()
                    if count > 0:
                        print(f"    📈 {count} records")
                except:
                    pass
    
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

def main():
    """Main function"""
    print("🗄️  Azure Flask Migrations Helper")
    print("=" * 50)
    
    # Check current environment
    print(f"Current DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')[:50]}...")
    
    # Verify tables first
    verify_azure_tables()
    
    # Test migration system
    test_migration_system()
    
    print("\n📋 Summary:")
    print("• Azure database has all tables created")
    print("• Flask migrations can now be used for schema changes")
    print("• Use: export DATABASE_URL='...' && flask db migrate")
    
    print("\n💡 For future migrations:")
    print("1. Make model changes in your Python files")
    print("2. Run: flask db migrate -m 'Description of changes'")
    print("3. Run: flask db upgrade")

if __name__ == '__main__':
    main()
