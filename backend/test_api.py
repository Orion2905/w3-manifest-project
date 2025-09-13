#!/usr/bin/env python3
"""
Test script for W3 Manifest API endpoints.
"""

import requests
import json
from datetime import datetime

# API base URL
BASE_URL = "http://127.0.0.1:5000/api"

def test_api_endpoints():
    """Test the W3 Manifest API endpoints."""
    
    print("Testing W3 Manifest API Endpoints")
    print("=" * 40)
    
    # Test health endpoint
    try:
        response = requests.get("http://127.0.0.1:5000/health")
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
    
    # Test root endpoint
    try:
        response = requests.get("http://127.0.0.1:5000/")
        print(f"✅ Root Endpoint: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('message')}")
            print(f"   Endpoints: {list(data.get('endpoints', {}).keys())}")
    except Exception as e:
        print(f"❌ Root Endpoint Failed: {e}")
    
    print("\n" + "=" * 40)
    print("API Tests Completed")
    print("=" * 40)
    
    print("\nNext Steps:")
    print("1. 🔐 Set up authentication (create admin user)")
    print("2. 📊 Test manifest upload with sample files")
    print("3. 🗂️ Test order management endpoints")
    print("4. 🎨 Build frontend interface")
    
    print("\nSample CURL commands:")
    print(f"curl -X GET {BASE_URL}/auth/health")
    print(f"curl -X POST {BASE_URL}/auth/register -H 'Content-Type: application/json' -d '{{\"email\":\"admin@w3group.it\",\"password\":\"admin123\",\"username\":\"admin\",\"first_name\":\"Admin\",\"last_name\":\"User\",\"role\":\"admin\"}}'")

if __name__ == "__main__":
    test_api_endpoints()
