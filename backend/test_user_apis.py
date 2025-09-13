#!/usr/bin/env python3
"""
Testa completamente le API di gestione utenti.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5001"

def test_user_management_apis():
    """Testa tutte le API di gestione utenti."""
    
    print("🧪 TESTING USER MANAGEMENT APIs")
    print("=" * 50)
    
    # 1. Login per ottenere il token
    print("\n1. 🔐 Testing Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return False
        
        login_result = response.json()
        token = login_result.get('access_token')
        if not token:
            print(f"❌ No token received: {login_result}")
            return False
        
        print("✅ Login successful!")
        headers = {"Authorization": f"Bearer {token}"}
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 2. Test User Stats
    print("\n2. 📊 Testing User Statistics...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Stats: {stats['total_users']} total users, {stats['active_users']} active")
        else:
            print(f"❌ Stats failed: {response.text}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    # 3. Test Get Users List
    print("\n3. 👥 Testing Get Users List...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
        if response.status_code == 200:
            users_data = response.json()
            users = users_data.get('users', [])
            print(f"✅ Found {len(users)} users")
            for user in users[:2]:  # Show first 2
                print(f"  - {user['username']} ({user['role_display']})")
        else:
            print(f"❌ Get users failed: {response.text}")
    except Exception as e:
        print(f"❌ Get users error: {e}")
    
    # 4. Test Create User
    print("\n4. ➕ Testing Create User...")
    new_user_data = {
        "username": "testmanager",
        "email": "manager@test.com",
        "password": "Manager123!",
        "first_name": "Test",
        "last_name": "Manager",
        "role_id": 2  # Manager role
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/admin/users", json=new_user_data, headers=headers)
        if response.status_code == 201:
            user_result = response.json()
            created_user = user_result.get('user')
            print(f"✅ User created: {created_user['username']} ({created_user['role']['display_name']})")
            user_id = created_user['id']
        else:
            print(f"❌ Create user failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Create user error: {e}")
        return False
    
    # 5. Test Get Specific User
    print(f"\n5. 🔍 Testing Get User {user_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            user = user_data.get('user')
            print(f"✅ Retrieved user: {user['username']} - {user['email']}")
        else:
            print(f"❌ Get user failed: {response.text}")
    except Exception as e:
        print(f"❌ Get user error: {e}")
    
    # 6. Test Update User
    print(f"\n6. ✏️ Testing Update User {user_id}...")
    update_data = {
        "first_name": "Updated",
        "department": "IT Department"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/api/admin/users/{user_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            update_result = response.json()
            updated_user = update_result.get('user')
            print(f"✅ User updated: {updated_user['first_name']} {updated_user['last_name']}")
        else:
            print(f"❌ Update user failed: {response.text}")
    except Exception as e:
        print(f"❌ Update user error: {e}")
    
    # 7. Test Toggle User Status
    print(f"\n7. 🔄 Testing Toggle User Status...")
    try:
        response = requests.patch(f"{BASE_URL}/api/admin/users/{user_id}/toggle-status", headers=headers)
        if response.status_code == 200:
            toggle_result = response.json()
            print(f"✅ Status toggled: {toggle_result.get('message')}")
        else:
            print(f"❌ Toggle status failed: {response.text}")
    except Exception as e:
        print(f"❌ Toggle status error: {e}")
    
    # 8. Test Delete User
    print(f"\n8. 🗑️ Testing Delete User...")
    try:
        response = requests.delete(f"{BASE_URL}/api/admin/users/{user_id}", headers=headers)
        if response.status_code == 200:
            delete_result = response.json()
            print(f"✅ User deleted: {delete_result.get('message')}")
        else:
            print(f"❌ Delete user failed: {response.text}")
    except Exception as e:
        print(f"❌ Delete user error: {e}")
    
    print("\n🎉 USER MANAGEMENT API TESTS COMPLETED!")
    return True

if __name__ == '__main__':
    success = test_user_management_apis()
    if not success:
        sys.exit(1)
