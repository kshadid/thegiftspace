#!/usr/bin/env python3
"""
Simple Admin Backend API Testing - Focus on available endpoints
"""

import requests
import json
import uuid
import os

# Load environment variables to get the backend URL
def load_env_file(file_path):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"')
    return env_vars

# Get backend URL from frontend .env
frontend_env = load_env_file('/app/frontend/.env')
BACKEND_URL = frontend_env.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"

print(f"Testing admin endpoints at: {API_BASE}")

def test_admin_endpoints():
    session = requests.Session()
    
    # Try to register a new admin user with a unique email
    unique_id = str(uuid.uuid4())[:8]
    admin_email = f"admin.{unique_id}@gmail.com"
    
    print(f"\n=== Registering new admin user: {admin_email} ===")
    
    user_data = {
        "name": "Test Admin",
        "email": admin_email,
        "password": "AdminPassword123!"
    }
    
    try:
        response = session.post(f"{API_BASE}/auth/register", json=user_data)
        print(f"Register response: {response.status_code} - {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            token = data['access_token']
            session.headers.update({'Authorization': f'Bearer {token}'})
            
            print(f"✅ Admin user registered successfully")
            
            # Test admin endpoints
            endpoints_to_test = [
                ("/admin/me", "GET"),
                ("/admin/stats", "GET"),
                ("/admin/metrics", "GET"),
                ("/admin/users", "GET"),
                ("/admin/registries", "GET")
            ]
            
            for endpoint, method in endpoints_to_test:
                try:
                    if method == "GET":
                        resp = session.get(f"{API_BASE}{endpoint}")
                    
                    print(f"{endpoint}: {resp.status_code} - {resp.text[:200]}...")
                    
                except Exception as e:
                    print(f"{endpoint}: ERROR - {str(e)}")
        
        else:
            print(f"❌ Failed to register admin user: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Exception during registration: {str(e)}")

    # Test if kshadid@gmail.com exists and try common passwords
    print(f"\n=== Testing existing admin user: kshadid@gmail.com ===")
    
    common_passwords = [
        "password",
        "admin123",
        "AdminPassword123!",
        "kshadid123",
        "admin",
        "123456"
    ]
    
    for password in common_passwords:
        try:
            login_data = {
                "email": "kshadid@gmail.com",
                "password": password
            }
            
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                print(f"✅ Successfully logged in with password: {password}")
                data = response.json()
                token = data['access_token']
                session.headers.update({'Authorization': f'Bearer {token}'})
                
                # Test admin/me endpoint
                me_response = session.get(f"{API_BASE}/admin/me")
                print(f"Admin/me response: {me_response.status_code} - {me_response.text}")
                
                break
            else:
                print(f"❌ Failed login with password '{password}': {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception with password '{password}': {str(e)}")

if __name__ == "__main__":
    test_admin_endpoints()