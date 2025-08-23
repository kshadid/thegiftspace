#!/usr/bin/env python3
"""
Quick test for login endpoint
"""

import requests
import json
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

print(f"Testing login at: {API_BASE}")

# First register a user
register_data = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "TestPass123!"
}

print("Registering user...")
response = requests.post(f"{API_BASE}/auth/register", json=register_data)
if response.status_code == 201:
    print("✅ User registered successfully")
elif response.status_code == 409:
    print("ℹ️ User already exists, proceeding with login test")
else:
    print(f"❌ Registration failed: {response.status_code} - {response.text}")

# Now test login
login_data = {
    "email": "testuser@example.com",
    "password": "TestPass123!"
}

print("Testing login...")
response = requests.post(f"{API_BASE}/auth/login", json=login_data)

if response.status_code == 200:
    data = response.json()
    if 'access_token' in data and 'user' in data:
        print("✅ Login successful!")
        print(f"Token type: {data.get('token_type')}")
        print(f"User: {data['user']['name']} ({data['user']['email']})")
    else:
        print(f"❌ Login response missing token or user: {data}")
else:
    print(f"❌ Login failed: {response.status_code} - {response.text}")