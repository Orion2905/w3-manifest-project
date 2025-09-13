#!/usr/bin/env python3
"""
Test specifico per il login.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User

def test_login_process():
    """Testa il processo di login."""
    app = create_app('production')
    
    with app.app_context():
        try:
            print("🧪 Testing login process...")
            
            # Trova l'utente admin
            user = User.query.filter_by(username='admin').first()
            if not user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Found user: {user.username}")
            
            # Test password
            if not user.check_password('admin123'):
                print("❌ Password check failed!")
                return False
            
            print("✅ Password check passed")
            
            # Test account status
            if not user.is_active:
                print("❌ User is not active!")
                return False
            
            print("✅ User is active")
            
            # Test role access
            if user.role_obj:
                print(f"✅ User has role: {user.role_obj.name}")
            else:
                print("⚠️ User has no role object")
            
            # Test JWT token creation
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=user.id)
            print(f"✅ JWT token created: {token[:50]}...")
            
            print("🎉 Login process test PASSED!")
            return True
            
        except Exception as e:
            print(f"❌ Login process test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_login_process()
    if not success:
        sys.exit(1)
