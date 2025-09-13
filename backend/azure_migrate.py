#!/usr/bin/env python3
"""
Azure Database Migration Script
Create all tables directly on Azure SQL Server using SQLAlchemy
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add current directory to path
sys.path.append('.')

# Database URL for Azure
AZURE_URL = "mssql+pyodbc://w3admin:W3Manifest2024!@w3manifest-sqlserver-prod.database.windows.net:1433/w3manifest-db?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no"

def create_all_tables():
    """Create all tables on Azure database"""
    print("🚀 Azure Database Migration Script")
    print("=" * 50)
    
    try:
        # Create engine
        engine = create_engine(AZURE_URL)
        
        # Test connection
        print("🔌 Testing connection to Azure...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.scalar()
            print(f"✅ Connected to: {version[:50]}...")
        
        # Import all models to register them with SQLAlchemy
        print("📦 Importing models...")
        from app import db
        from app.models import user, order, manifest_email, audit_log, rbac, email_config
        
        # Create all tables
        print("🔨 Creating all tables...")
        db.metadata.create_all(engine)
        
        # Verify tables created
        print("📊 Verifying tables...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT TABLE_NAME, 
                       (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = t.TABLE_NAME) as COLUMN_COUNT
                FROM INFORMATION_SCHEMA.TABLES t
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            
            tables = result.fetchall()
            print(f"✅ Created {len(tables)} tables:")
            
            for table_name, column_count in tables:
                print(f"  📋 {table_name} ({column_count} columns)")
                
                # Count records if table has data
                try:
                    count_result = conn.execute(text(f"SELECT COUNT(*) FROM [{table_name}]"))
                    count = count_result.scalar()
                    if count > 0:
                        print(f"     📈 {count} records")
                except:
                    pass  # Some tables might be empty or have constraints
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def seed_rbac_data():
    """Seed RBAC data"""
    print("\n🌱 Seeding RBAC data...")
    
    try:
        # Import and use existing seed function
        from app.models.seeds import seed_rbac_data as seed_func
        
        # Set up Flask app context for seeding
        from app import create_app, db
        import os
        
        # Force production config with Azure
        os.environ['DATABASE_URL'] = AZURE_URL
        os.environ['FLASK_ENV'] = 'production'
        
        app = create_app('production')
        with app.app_context():
            # Override database URL to use Azure
            app.config['SQLALCHEMY_DATABASE_URI'] = AZURE_URL
            
            # Initialize db with Azure URL
            db.engine = create_engine(AZURE_URL)
            
            result = seed_func()
            print(f"✅ RBAC seeded: {result['permissions']} permissions, {result['roles']} roles")
            
    except Exception as e:
        print(f"❌ RBAC seeding failed: {e}")

def main():
    """Main function"""
    if create_all_tables():
        seed_rbac_data()
        
        print("\n📋 Next steps:")
        print("1. Update your .env file with Azure database URL")
        print("2. Set FLASK_ENV=production")
        print("3. Start your Flask application")
        print("\n🔧 Test connection with:")
        print("python test_azure_final.py")
    else:
        print("\n❌ Migration failed. Check the error messages above.")

if __name__ == '__main__':
    main()
