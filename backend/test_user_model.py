#!/usr/bin/env python3
"""
Test rapido per verificare problemi con il modello User.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User

def test_user_model():
    """Testa il modello User."""
    app = create_app('production')
    
    with app.app_context():
        try:
            # Test query semplice
            print("🧪 Testing User model...")
            users = User.query.all()
            print(f"✅ Found {len(users)} users")
            
            if users:
                user = users[0]
                print(f"✅ First user: {user.username}")
                print(f"✅ Role obj: {user.role_obj}")
                print(f"✅ Role name: {user.role_obj.name if user.role_obj else 'No role'}")
                
                # Test to_dict method
                user_dict = user.to_dict()
                print(f"✅ to_dict() works: {user_dict['username']}")
                
                # Test password check
                valid = user.check_password('admin123')
                print(f"✅ Password check works: {valid}")
                
            print("🎉 User model test PASSED!")
            return True
            
        except Exception as e:
            print(f"❌ User model test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_user_model()
    if not success:
        sys.exit(1)
