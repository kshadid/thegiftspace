#!/usr/bin/env python3
"""
Focused Rate Limiting Test
"""

import requests
import json
import uuid
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

print(f"Testing rate limiting at: {API_BASE}")

def make_login_request(login_data, request_num):
    """Make a single login request"""
    try:
        session = requests.Session()
        response = session.post(f"{API_BASE}/auth/login", json=login_data, timeout=10)
        return {
            'request_num': request_num,
            'status_code': response.status_code,
            'response_text': response.text[:100] if response.text else ''
        }
    except Exception as e:
        return {
            'request_num': request_num,
            'status_code': 'ERROR',
            'response_text': str(e)
        }

def test_rate_limiting():
    """Test rate limiting with concurrent requests"""
    
    # First, register a user
    unique_id = str(uuid.uuid4())[:8]
    user_data = {
        "name": "Rate Test User",
        "email": f"ratetest{unique_id}@example.com",
        "password": "testpassword123"
    }
    
    session = requests.Session()
    
    try:
        # Register user
        response = session.post(f"{API_BASE}/auth/register", json=user_data)
        
        if response.status_code != 201:
            print(f"❌ Failed to register user: {response.status_code} - {response.text}")
            return False
        
        print(f"✅ User registered: {user_data['email']}")
        
        # Prepare login data
        login_data = {
            "email": user_data['email'],
            "password": user_data['password']
        }
        
        # Test 1: Sequential requests (should work fine)
        print("\n=== Test 1: Sequential Requests (should pass) ===")
        for i in range(5):
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            print(f"Request {i+1}: {response.status_code}")
            time.sleep(0.1)
        
        # Test 2: Rapid sequential requests (should hit rate limit)
        print("\n=== Test 2: Rapid Sequential Requests ===")
        rate_limit_hit = False
        
        for i in range(25):
            response = session.post(f"{API_BASE}/auth/login", json=login_data)
            print(f"Request {i+1}: {response.status_code}")
            
            if response.status_code == 429:
                print(f"✅ Rate limit hit on request {i+1}")
                rate_limit_hit = True
                break
            elif response.status_code != 200:
                print(f"⚠️  Unexpected status: {response.status_code} - {response.text[:100]}")
        
        if not rate_limit_hit:
            print("❌ Rate limit not hit with sequential requests")
        
        # Test 3: Concurrent requests (more likely to hit rate limit)
        print("\n=== Test 3: Concurrent Requests ===")
        
        # Wait a bit for rate limit to reset
        time.sleep(2)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Submit 30 concurrent requests
            futures = [executor.submit(make_login_request, login_data, i+1) for i in range(30)]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"Request {result['request_num']}: {result['status_code']}")
                
                if result['status_code'] == 429:
                    print(f"✅ Rate limit hit on concurrent request {result['request_num']}")
                    rate_limit_hit = True
        
        return rate_limit_hit
        
    except Exception as e:
        print(f"❌ Exception during rate limit test: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_rate_limiting()
    if success:
        print("\n✅ Rate limiting test PASSED")
    else:
        print("\n❌ Rate limiting test FAILED")
    exit(0 if success else 1)