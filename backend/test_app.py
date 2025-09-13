#!/usr/bin/env python3
"""
Test the Flask application startup and basic functionality.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import after adding to path
from app import create_app, db
from app.models.user import User
from app.models.order import Order
from app.models.manifest_email import ManifestEmail

def test_app_creation():
    """Test that the Flask app can be created."""
    print("Testing Flask app creation...")
    
    try:
        app = create_app('development')
        print("✅ Flask app created successfully")
        
        with app.app_context():
            # Test database connection
            print("Testing database connection...")
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Test model creation
            print("Testing model creation...")
            user = User(
                username="testuser",
                email="test@example.com",
                password="testpassword",
                first_name="Test",
                last_name="User",
                role="operator"
            )
            
            print("✅ User model created successfully")
            
            manifest = ManifestEmail(
                email_subject="Test Manifest",
                email_sender="test@classicvacations.com",
                email_date=datetime.utcnow(),
                email_message_id="test123",
                received_at=datetime.utcnow(),
                status="pending"
            )
            
            print("✅ ManifestEmail model created successfully")
            
            order = Order(
                service_id="TEST123",
                service_date=datetime.utcnow().date(),
                action="new",
                service_type="transfer",
                description="Test transfer service",
                status="pending",
                created_by_user_id=1  # Will be set properly when user is saved
            )
            
            print("✅ Order model created successfully")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    return True

def test_endpoints():
    """Test that endpoints are registered correctly."""
    print("\nTesting endpoint registration...")
    
    try:
        app = create_app('development')
        
        with app.test_client() as client:
            # Test root endpoint
            response = client.get('/')
            print(f"Root endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"Available endpoints: {data.get('endpoints', {})}")
                print("✅ Root endpoint working")
            
            # Test health endpoint
            response = client.get('/health')
            print(f"Health endpoint status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Health endpoint working")
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {str(e)}")
        return False
    
    return True

def test_manifest_parser():
    """Test the manifest parser with a simple case."""
    print("\nTesting manifest parser...")
    
    try:
        from app.services.manifest_parser import ManifestParser, ParsedService
        
        parser = ManifestParser()
        
        # Test with simple text content
        test_content = """
        [New] 15-Jul-25 Transfer - Naples to Rome by Mercedes E for 1-2
        Adult 1: Mr. John Doe
        Cell Phone: +1234567890
        pick up 9:00 am
        Flight: LH123
        """
        
        # Parse the content directly
        services = parser.parse_manifest_content(test_content)
        
        print(f"Parsed {len(services)} services")
        
        if services:
            service = services[0]
            print(f"Action: {service.action}")
            print(f"Date: {service.service_date}")
            print(f"Vehicle: {service.vehicle_model}")
            print(f"Phone: {service.contact_phone}")
            print("✅ Manifest parser working")
        else:
            print("⚠️  No services parsed from test content")
        
    except Exception as e:
        print(f"❌ Error testing manifest parser: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("W3 Manifest System - Basic Tests")
    print("=" * 40)
    
    success = True
    
    # Test app creation
    success &= test_app_creation()
    
    # Test endpoints
    success &= test_endpoints()
    
    # Test manifest parser
    success &= test_manifest_parser()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All basic tests passed!")
        print("\nYou can now:")
        print("1. Run the Flask development server: python app.py")
        print("2. Test the API endpoints with a REST client")
        print("3. Upload manifest files via the /api/manifest/upload endpoint")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    print("=" * 40)
