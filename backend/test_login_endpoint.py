#!/usr/bin/env python3
"""
Test del login endpoint direttamente.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
import json

def test_login_endpoint():
    """Testa l'endpoint di login direttamente."""
    app = create_app('production')
    
    with app.test_client() as client:
        try:
            print("🧪 Testing login endpoint directly...")
            
            # Simula una richiesta POST al login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            
            if response.status_code == 200:
                print("✅ Login endpoint works!")
                return True
            else:
                print("❌ Login endpoint failed!")
                return False
            
        except Exception as e:
            print(f"❌ Login endpoint test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_login_endpoint()
    if not success:
        sys.exit(1)
