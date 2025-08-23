#!/usr/bin/env python3
"""
Test admin lock functionality and admin access to contributions/audit
"""

import requests
import json
import uuid
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

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

print(f"Testing admin lock and access endpoints at: {API_BASE}")

def test_admin_lock_and_access():
    session = requests.Session()
    
    # Setup admin user
    async def setup_admin():
        try:
            mongo_url = 'mongodb://localhost:27017'
            client = AsyncIOMotorClient(mongo_url)
            db = client['test_database']
            
            # Delete existing admin user
            await db.users.delete_one({"email": "kshadid@gmail.com"})
            
            client.close()
            print("✅ Cleaned up existing admin user")
            
        except Exception as e:
            print(f"⚠️ Could not clean up existing user: {str(e)}")
    
    asyncio.run(setup_admin())
    
    # Register admin user
    user_data = {
        "name": "Khalid Shadid",
        "email": "kshadid@gmail.com",
        "password": "AdminPassword123!"
    }
    
    response = session.post(f"{API_BASE}/auth/register", json=user_data)
    if response.status_code != 201:
        print(f"❌ Failed to register admin: {response.status_code} - {response.text}")
        return
    
    admin_data = response.json()
    admin_token = admin_data['access_token']
    session.headers.update({'Authorization': f'Bearer {admin_token}'})
    
    print("✅ Admin user registered and authenticated")
    
    # Get a registry to test with
    registries_response = session.get(f"{API_BASE}/admin/registries")
    if registries_response.status_code != 200:
        print(f"❌ Could not get registries: {registries_response.status_code}")
        return
    
    registries = registries_response.json()
    if not registries:
        print("❌ No registries available to test with")
        return
    
    registry_id = registries[0]['id']
    print(f"✅ Using registry {registry_id} for testing")
    
    # Test 1: Admin lock functionality
    print(f"\n=== Test 1: Admin Lock Functionality ===")
    
    # Lock the registry
    lock_data = {"locked": True, "reason": "Testing lock functionality"}
    lock_response = session.post(f"{API_BASE}/admin/registries/{registry_id}/lock", json=lock_data)
    
    if lock_response.status_code == 200:
        lock_result = lock_response.json()
        if lock_result.get('ok'):
            print("✅ Registry locked successfully")
            
            # Unlock the registry
            unlock_data = {"locked": False}
            unlock_response = session.post(f"{API_BASE}/admin/registries/{registry_id}/lock", json=unlock_data)
            
            if unlock_response.status_code == 200:
                unlock_result = unlock_response.json()
                if unlock_result.get('ok'):
                    print("✅ Registry unlocked successfully")
                    print("✅ Admin lock/unlock functionality working")
                else:
                    print(f"❌ Unlock failed: {unlock_result}")
            else:
                print(f"❌ Unlock request failed: {unlock_response.status_code} - {unlock_response.text}")
        else:
            print(f"❌ Lock failed: {lock_result}")
    else:
        print(f"❌ Lock request failed: {lock_response.status_code} - {lock_response.text}")
    
    # Test 2: Admin access to contributions
    print(f"\n=== Test 2: Admin Access to Contributions ===")
    
    contributions_response = session.get(f"{API_BASE}/registries/{registry_id}/contributions")
    
    if contributions_response.status_code == 200:
        contributions = contributions_response.json()
        print(f"✅ Admin can access contributions: {len(contributions)} found")
    elif contributions_response.status_code == 404:
        print("❌ Contributions endpoint not found (404)")
    else:
        print(f"❌ Contributions access failed: {contributions_response.status_code} - {contributions_response.text}")
    
    # Test 3: Admin access to audit logs
    print(f"\n=== Test 3: Admin Access to Audit Logs ===")
    
    audit_response = session.get(f"{API_BASE}/registries/{registry_id}/audit")
    
    if audit_response.status_code == 200:
        audit_logs = audit_response.json()
        print(f"✅ Admin can access audit logs: {len(audit_logs)} found")
    elif audit_response.status_code == 404:
        print("❌ Audit endpoint not found (404)")
    else:
        print(f"❌ Audit access failed: {audit_response.status_code} - {audit_response.text}")

if __name__ == "__main__":
    test_admin_lock_and_access()