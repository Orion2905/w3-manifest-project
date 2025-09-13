#!/usr/bin/env python3
"""
Azure SQL Server Connection Tester
Test diversi formati di connessione per Azure SQL Server
"""

import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text
import urllib.parse

# Configurazioni database
SERVER = 'w3manifest-sqlserver-prod.database.windows.net'
DATABASE = 'w3manifest-db'
USERNAME = 'w3admin'
PASSWORD = 'W3Manifest2024!'

def test_odbc_connection():
    """Test connessione ODBC diretta"""
    print("🔌 Test ODBC Connection...")
    print("=" * 50)
    
    try:
        # Stringa ODBC
        connection_string = f"""
        Driver={{ODBC Driver 18 for SQL Server}};
        Server=tcp:{SERVER},1433;
        Database={DATABASE};
        Uid={USERNAME};
        Pwd={PASSWORD};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
        """
        
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT COUNT(*) as table_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        result = cursor.fetchone()
        
        print(f"✅ ODBC Connection successful!")
        print(f"📊 Tables found: {result[0]}")
        
        # Lista tabelle
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME")
        tables = cursor.fetchall()
        print(f"📋 Tables:")
        for table in tables:
            print(f"  • {table[0]}")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ ODBC Error: {e}")
        return False

def test_sqlalchemy_connection():
    """Test connessione SQLAlchemy"""
    print("\n🔌 Test SQLAlchemy Connection...")
    print("=" * 50)
    
    try:
        # URL per SQLAlchemy con pyodbc
        params = urllib.parse.quote_plus(f"""
        Driver={{ODBC Driver 18 for SQL Server}};
        Server=tcp:{SERVER},1433;
        Database={DATABASE};
        Uid={USERNAME};
        Pwd={PASSWORD};
        Encrypt=yes;
        TrustServerCertificate=no;
        Connection Timeout=30;
        """)
        
        url = f"mssql+pyodbc:///?odbc_connect={params}"
        engine = create_engine(url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as table_count FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
            count = result.scalar()
            
            print(f"✅ SQLAlchemy Connection successful!")
            print(f"📊 Tables found: {count}")
            
            # Lista tabelle
            result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME"))
            tables = result.fetchall()
            print(f"📋 Tables:")
            for table in tables:
                print(f"  • {table[0]}")
                
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy Error: {e}")
        return False

def test_simple_connection():
    """Test connessione semplificata"""
    print("\n🔌 Test Simple Connection String...")
    print("=" * 50)
    
    try:
        # Stringa semplificata
        connection_string = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
        
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.scalar()
            
            print(f"✅ Simple Connection successful!")
            print(f"🗄️ SQL Server Version: {version[:100]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Simple Connection Error: {e}")
        return False

def generate_connection_strings():
    """Genera diverse stringhe di connessione"""
    print("\n📋 Connection Strings Reference")
    print("=" * 60)
    
    print("🔧 Per SSMS/Azure Data Studio:")
    print(f"  Server: {SERVER}")
    print(f"  Database: {DATABASE}")
    print(f"  Username: {USERNAME}")
    print(f"  Password: {PASSWORD}")
    
    print("\n🔧 ODBC Connection String:")
    odbc_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    print(f"  {odbc_string}")
    
    print("\n🔧 SQLAlchemy URL (con pyodbc):")
    sqlalchemy_string = f"mssql+pyodbc://{USERNAME}:{PASSWORD}@{SERVER}:1433/{DATABASE}?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"
    print(f"  {sqlalchemy_string}")
    
    print("\n🔧 Flask/Django Connection String:")
    flask_string = f"Server=tcp:{SERVER},1433;Initial Catalog={DATABASE};Persist Security Info=False;User ID={USERNAME};Password={PASSWORD};MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"
    print(f"  {flask_string}")

def main():
    """Main function"""
    print("🗄️  Azure SQL Server - Connection Tester")
    print("=" * 60)
    print(f"🎯 Target: {SERVER}")
    print(f"📊 Database: {DATABASE}")
    print(f"👤 User: {USERNAME}")
    
    # Test diverse connessioni
    odbc_ok = test_odbc_connection()
    sqlalchemy_ok = test_sqlalchemy_connection()
    simple_ok = test_simple_connection()
    
    # Genera stringhe di riferimento
    generate_connection_strings()
    
    # Riepilogo
    print(f"\n📊 Connection Test Results")
    print("=" * 30)
    print(f"ODBC: {'✅' if odbc_ok else '❌'}")
    print(f"SQLAlchemy: {'✅' if sqlalchemy_ok else '❌'}")
    print(f"Simple: {'✅' if simple_ok else '❌'}")
    
    if odbc_ok or sqlalchemy_ok or simple_ok:
        print(f"\n🎉 Database is accessible! Tables are present.")
        print(f"💡 If you can't see tables in your SQL tool, check:")
        print(f"   • Firewall settings")
        print(f"   • Client tool configuration")
        print(f"   • Database/schema selection")
    else:
        print(f"\n⚠️  All connections failed. Check:")
        print(f"   • Network connectivity")
        print(f"   • Server firewall")
        print(f"   • Credentials")

if __name__ == '__main__':
    main()
