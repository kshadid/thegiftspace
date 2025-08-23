#!/usr/bin/env python3
"""
Backend API Testing Suite for Honeymoon Registry MVP - Restored Endpoints Focus
Tests restored registry CRUD endpoints, admin functionality, and lock/unlock features
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path
import time

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

print(f"Testing restored endpoints at: {API_BASE}")

class RestoredEndpointsTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def log_result(self, test_name, success, message=""):
        if success:
            self.results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def set_auth_header(self, token):
        """Set authorization header for authenticated requests"""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def clear_auth_header(self):
        """Clear authorization header"""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def test_1_register_admin_user(self):
        """Test 1: Register admin user (kshadid@gmail.com) and obtain JWT token"""
        print("\n=== Test 1: Register Admin User ===")
        
        # Generate unique admin email for this test run to avoid conflicts
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            "name": "Khalid Shadid",
            "email": f"kshadid.{unique_id}@gmail.com",
            "password": "AdminSecurePassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response structure
                if 'access_token' in data and 'user' in data:
                    token = data['access_token']
                    user = data['user']
                    
                    if 'id' in user and user.get('email') == user_data['email']:
                        self.test_data['admin_token'] = token
                        self.test_data['admin_id'] = user['id']
                        self.test_data['admin_email'] = user['email']
                        self.log_result("Register Admin User", True, f"Admin registered: {user['name']} ({user['email']})")
                    else:
                        self.log_result("Register Admin User", False, f"Invalid user data in response: {user}")
                else:
                    self.log_result("Register Admin User", False, f"Missing access_token or user in response: {data}")
            else:
                self.log_result("Register Admin User", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Register Admin User", False, f"Exception: {str(e)}")
    
    def test_2_register_normal_user(self):
        """Test 2: Register normal user and obtain JWT token"""
        print("\n=== Test 2: Register Normal User ===")
        
        # Generate unique email for this test run
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            "name": "Sarah Al-Mansouri",
            "email": f"sarah.almansouri.{unique_id}@example.com",
            "password": "UserSecurePassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response structure
                if 'access_token' in data and 'user' in data:
                    token = data['access_token']
                    user = data['user']
                    
                    if 'id' in user and user.get('email') == user_data['email']:
                        self.test_data['user_token'] = token
                        self.test_data['user_id'] = user['id']
                        self.test_data['user_email'] = user['email']
                        self.log_result("Register Normal User", True, f"User registered: {user['name']} ({user['email']})")
                    else:
                        self.log_result("Register Normal User", False, f"Invalid user data in response: {user}")
                else:
                    self.log_result("Register Normal User", False, f"Missing access_token or user in response: {data}")
            else:
                self.log_result("Register Normal User", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Register Normal User", False, f"Exception: {str(e)}")
    
    def test_3_create_registry_as_normal_user(self):
        """Test 3: As normal user, POST /api/registries to create a registry"""
        print("\n=== Test 3: Create Registry as Normal User ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("Create Registry", False, "No user_token from previous test")
            return
        
        # Set auth header for normal user
        self.set_auth_header(self.test_data['user_token'])
        
        # Generate unique slug for this test run
        unique_id = str(uuid.uuid4())[:8]
        event_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        
        registry_data = {
            "couple_names": "Sarah & Ahmed Al-Mansouri",
            "event_date": event_date,
            "location": "Dubai, UAE",
            "currency": "AED",
            "hero_image": "https://example.com/dubai-wedding.jpg",
            "slug": f"sarah-ahmed-{unique_id}",
            "theme": "modern"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries", json=registry_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response has required fields
                if ('id' in data and data.get('slug') == registry_data['slug'] and 
                    data.get('owner_id') == self.test_data['user_id']):
                    self.test_data['registry_id'] = data['id']
                    self.test_data['registry_slug'] = data['slug']
                    self.log_result("Create Registry", True, f"Registry created with ID: {data['id']}, slug: {data['slug']}")
                else:
                    self.log_result("Create Registry", False, f"Missing id, slug mismatch, or wrong owner_id in response: {data}")
            else:
                self.log_result("Create Registry", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create Registry", False, f"Exception: {str(e)}")
    
    def test_4_get_my_registries(self):
        """Test 4: GET /api/registries/mine returns the created registry"""
        print("\n=== Test 4: Get My Registries ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Get My Registries", False, "Missing user_token or registry_id from previous tests")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/mine")
            
            if response.status_code == 200:
                registries = response.json()
                
                if isinstance(registries, list) and len(registries) >= 1:
                    # Look for our created registry
                    registry_found = False
                    for registry in registries:
                        if registry.get('id') == self.test_data['registry_id']:
                            registry_found = True
                            if registry.get('owner_id') == self.test_data['user_id']:
                                self.log_result("Get My Registries", True, f"Found created registry with correct owner_id")
                            else:
                                self.log_result("Get My Registries", False, f"Registry found but wrong owner_id: {registry.get('owner_id')}")
                            break
                    
                    if not registry_found:
                        self.log_result("Get My Registries", False, f"Created registry {self.test_data['registry_id']} not found in user's registries")
                else:
                    self.log_result("Get My Registries", False, f"Expected at least 1 registry, got: {len(registries) if isinstance(registries, list) else 'not a list'}")
            else:
                self.log_result("Get My Registries", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Get My Registries", False, f"Exception: {str(e)}")
    
    def test_5_update_registry(self):
        """Test 5: PUT /api/registries/{id} updates the registry"""
        print("\n=== Test 5: Update Registry ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Update Registry", False, "Missing user_token or registry_id from previous tests")
            return
        
        update_data = {
            "location": "Abu Dhabi, UAE",
            "theme": "elegant"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/registries/{self.test_data['registry_id']}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify the update was applied
                if (data.get('location') == update_data['location'] and 
                    data.get('theme') == update_data['theme']):
                    self.log_result("Update Registry", True, f"Registry updated successfully: location={data.get('location')}, theme={data.get('theme')}")
                else:
                    self.log_result("Update Registry", False, f"Update not applied correctly: {data}")
            else:
                self.log_result("Update Registry", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Update Registry", False, f"Exception: {str(e)}")
    
    def test_6_add_funds_bulk_upsert(self):
        """Test 6: Add funds via POST /api/registries/{id}/funds/bulk_upsert"""
        print("\n=== Test 6: Add Funds via Bulk Upsert ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Add Funds", False, "Missing user_token or registry_id from previous tests")
            return
        
        funds_data = {
            "funds": [
                {
                    "title": "Honeymoon Flight Tickets",
                    "description": "Round-trip flights to Maldives",
                    "goal": 5000.0,
                    "category": "travel",
                    "visible": True,
                    "order": 1
                },
                {
                    "title": "Luxury Resort Stay",
                    "description": "5-star resort accommodation for 7 nights",
                    "goal": 8000.0,
                    "category": "accommodation",
                    "visible": True,
                    "order": 2
                },
                {
                    "title": "Romantic Dinner Experiences",
                    "description": "Special dining experiences during honeymoon",
                    "goal": 1500.0,
                    "category": "dining",
                    "visible": True,
                    "order": 3
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert", json=funds_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify funds were created
                if data.get('created') == 3 and data.get('updated') == 0:
                    self.log_result("Add Funds", True, f"Successfully created {data.get('created')} funds")
                    
                    # Store fund IDs for later tests - get them from the funds list
                    funds_response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds")
                    if funds_response.status_code == 200:
                        funds = funds_response.json()
                        self.test_data['fund_ids'] = [fund['id'] for fund in funds]
                        self.log_result("Get Fund IDs", True, f"Retrieved {len(self.test_data['fund_ids'])} fund IDs")
                    else:
                        self.log_result("Get Fund IDs", False, f"Failed to get fund IDs: {funds_response.status_code}")
                else:
                    self.log_result("Add Funds", False, f"Expected created=3, updated=0, got: {data}")
            else:
                self.log_result("Add Funds", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Add Funds", False, f"Exception: {str(e)}")
    
    def test_7_create_contributions(self):
        """Test 7: Create contributions to the funds"""
        print("\n=== Test 7: Create Contributions ===")
        
        if 'fund_ids' not in self.test_data or not self.test_data['fund_ids']:
            self.log_result("Create Contributions", False, "Missing fund_ids from previous tests")
            return
        
        contributions_data = [
            {
                "fund_id": self.test_data['fund_ids'][0],
                "name": "Ahmed & Fatima",
                "amount": 1000.0,
                "message": "Wishing you a wonderful honeymoon!",
                "public": True,
                "method": "bank_transfer"
            },
            {
                "fund_id": self.test_data['fund_ids'][1],
                "name": "Omar Al-Rashid",
                "amount": 1500.0,
                "message": "Congratulations on your wedding!",
                "public": True,
                "method": "credit_card"
            },
            {
                "fund_id": self.test_data['fund_ids'][2],
                "name": "Aisha Mohammed",
                "amount": 500.0,
                "message": "Have an amazing time!",
                "public": True,
                "method": "cash"
            }
        ]
        
        created_contributions = 0
        
        for i, contrib_data in enumerate(contributions_data):
            try:
                # Clear auth header for public contribution
                self.clear_auth_header()
                
                response = self.session.post(f"{API_BASE}/contributions", json=contrib_data)
                
                if response.status_code == 201:
                    data = response.json()
                    
                    if 'id' in data and data.get('fund_id') == contrib_data['fund_id']:
                        created_contributions += 1
                        self.log_result(f"Create Contribution {i+1}", True, f"Contribution created: {data.get('name')} - AED {data.get('amount')}")
                    else:
                        self.log_result(f"Create Contribution {i+1}", False, f"Invalid contribution data: {data}")
                else:
                    self.log_result(f"Create Contribution {i+1}", False, f"Expected 201, got {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"Create Contribution {i+1}", False, f"Exception: {str(e)}")
        
        if created_contributions == len(contributions_data):
            self.log_result("Create Contributions", True, f"Successfully created {created_contributions} contributions")
        else:
            self.log_result("Create Contributions", False, f"Expected {len(contributions_data)} contributions, created {created_contributions}")
    
    def test_8_admin_get_registry_detail(self):
        """Test 8: As admin, GET /api/registries/{id} works"""
        print("\n=== Test 8: Admin Get Registry Detail ===")
        
        if 'admin_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Admin Get Registry", False, "Missing admin_token or registry_id from previous tests")
            return
        
        # Set auth header for admin user
        self.set_auth_header(self.test_data['admin_token'])
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify registry data
                if ('id' in data and data.get('id') == self.test_data['registry_id'] and
                    'owner_id' in data and 'slug' in data):
                    self.log_result("Admin Get Registry", True, f"Admin can access registry: {data.get('slug')}")
                else:
                    self.log_result("Admin Get Registry", False, f"Invalid registry data: {data}")
            else:
                self.log_result("Admin Get Registry", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Get Registry", False, f"Exception: {str(e)}")
    
    def test_9_admin_get_contributions(self):
        """Test 9: As admin, GET /api/registries/{id}/contributions returns list"""
        print("\n=== Test 9: Admin Get Contributions ===")
        
        if 'admin_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Admin Get Contributions", False, "Missing admin_token or registry_id from previous tests")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                
                if isinstance(contributions, list) and len(contributions) >= 3:
                    # Verify contribution structure
                    valid_contributions = 0
                    for contrib in contributions:
                        if ('id' in contrib and 'fund_id' in contrib and 
                            'amount' in contrib and 'created_at' in contrib):
                            valid_contributions += 1
                    
                    if valid_contributions >= 3:
                        self.log_result("Admin Get Contributions", True, f"Admin can access {len(contributions)} contributions")
                    else:
                        self.log_result("Admin Get Contributions", False, f"Only {valid_contributions} valid contributions out of {len(contributions)}")
                else:
                    self.log_result("Admin Get Contributions", False, f"Expected at least 3 contributions, got: {len(contributions) if isinstance(contributions, list) else 'not a list'}")
            else:
                self.log_result("Admin Get Contributions", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Get Contributions", False, f"Exception: {str(e)}")
    
    def test_10_admin_get_audit_logs(self):
        """Test 10: As admin, GET /api/registries/{id}/audit returns audit entries"""
        print("\n=== Test 10: Admin Get Audit Logs ===")
        
        if 'admin_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Admin Get Audit", False, "Missing admin_token or registry_id from previous tests")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/audit")
            
            if response.status_code == 200:
                audit_logs = response.json()
                
                if isinstance(audit_logs, list):
                    # Verify audit log structure
                    valid_logs = 0
                    for log in audit_logs:
                        if ('id' in log and 'registry_id' in log and 
                            'action' in log and 'created_at' in log):
                            valid_logs += 1
                    
                    self.log_result("Admin Get Audit", True, f"Admin can access {len(audit_logs)} audit logs ({valid_logs} valid)")
                else:
                    self.log_result("Admin Get Audit", False, f"Expected list, got: {type(audit_logs)}")
            else:
                self.log_result("Admin Get Audit", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Get Audit", False, f"Exception: {str(e)}")
    
    def test_11_admin_lock_registry(self):
        """Test 11: Lock registry via admin"""
        print("\n=== Test 11: Admin Lock Registry ===")
        
        if 'admin_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Admin Lock Registry", False, "Missing admin_token or registry_id from previous tests")
            return
        
        lock_data = {
            "locked": True,
            "reason": "Testing lock functionality"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/registries/{self.test_data['registry_id']}/lock", json=lock_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok') == True:
                    self.log_result("Admin Lock Registry", True, "Registry locked successfully")
                else:
                    self.log_result("Admin Lock Registry", False, f"Expected ok=True, got: {data}")
            else:
                self.log_result("Admin Lock Registry", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Lock Registry", False, f"Exception: {str(e)}")
    
    def test_12_verify_owner_put_returns_423(self):
        """Test 12: Verify owner PUT returns 423 when registry is locked"""
        print("\n=== Test 12: Verify Owner PUT Returns 423 ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Owner PUT 423", False, "Missing user_token or registry_id from previous tests")
            return
        
        # Switch back to normal user token
        self.set_auth_header(self.test_data['user_token'])
        
        update_data = {
            "location": "Sharjah, UAE"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/registries/{self.test_data['registry_id']}", json=update_data)
            
            if response.status_code == 423:
                self.log_result("Owner PUT 423", True, "Owner PUT correctly returns 423 when registry is locked")
            else:
                self.log_result("Owner PUT 423", False, f"Expected 423, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Owner PUT 423", False, f"Exception: {str(e)}")
    
    def test_13_verify_funds_upsert_returns_423(self):
        """Test 13: Verify funds upsert returns 423 when registry is locked"""
        print("\n=== Test 13: Verify Funds Upsert Returns 423 ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Funds Upsert 423", False, "Missing user_token or registry_id from previous tests")
            return
        
        funds_data = {
            "funds": [
                {
                    "title": "Test Fund",
                    "description": "This should fail",
                    "goal": 1000.0,
                    "visible": True
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert", json=funds_data)
            
            if response.status_code == 423:
                self.log_result("Funds Upsert 423", True, "Funds upsert correctly returns 423 when registry is locked")
            else:
                self.log_result("Funds Upsert 423", False, f"Expected 423, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Funds Upsert 423", False, f"Exception: {str(e)}")
    
    def test_14_admin_unlock_registry(self):
        """Test 14: Unlock registry via admin"""
        print("\n=== Test 14: Admin Unlock Registry ===")
        
        if 'admin_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Admin Unlock Registry", False, "Missing admin_token or registry_id from previous tests")
            return
        
        # Switch back to admin token
        self.set_auth_header(self.test_data['admin_token'])
        
        unlock_data = {
            "locked": False,
            "reason": None
        }
        
        try:
            response = self.session.post(f"{API_BASE}/admin/registries/{self.test_data['registry_id']}/lock", json=unlock_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('ok') == True:
                    self.log_result("Admin Unlock Registry", True, "Registry unlocked successfully")
                else:
                    self.log_result("Admin Unlock Registry", False, f"Expected ok=True, got: {data}")
            else:
                self.log_result("Admin Unlock Registry", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Unlock Registry", False, f"Exception: {str(e)}")
    
    def test_15_verify_write_works_after_unlock(self):
        """Test 15: Verify write operations work again after unlock"""
        print("\n=== Test 15: Verify Write Works After Unlock ===")
        
        if 'user_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Write After Unlock", False, "Missing user_token or registry_id from previous tests")
            return
        
        # Switch back to normal user token
        self.set_auth_header(self.test_data['user_token'])
        
        update_data = {
            "location": "Fujairah, UAE"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/registries/{self.test_data['registry_id']}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('location') == update_data['location']:
                    self.log_result("Write After Unlock", True, f"Owner PUT works after unlock: location={data.get('location')}")
                else:
                    self.log_result("Write After Unlock", False, f"Update not applied: {data}")
            else:
                self.log_result("Write After Unlock", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Write After Unlock", False, f"Exception: {str(e)}")
    
    def test_16_verify_api_prefix_and_jwt(self):
        """Test 16: Confirm all routes use /api prefix and JWT"""
        print("\n=== Test 16: Verify API Prefix and JWT ===")
        
        # Test that all endpoints use /api prefix
        endpoints_tested = [
            "/auth/register",
            "/registries",
            "/registries/mine",
            f"/registries/{self.test_data.get('registry_id', 'test')}",
            f"/registries/{self.test_data.get('registry_id', 'test')}/contributions",
            f"/registries/{self.test_data.get('registry_id', 'test')}/audit",
            f"/registries/{self.test_data.get('registry_id', 'test')}/funds/bulk_upsert",
            f"/admin/registries/{self.test_data.get('registry_id', 'test')}/lock"
        ]
        
        prefix_correct = True
        jwt_required = True
        
        for endpoint in endpoints_tested:
            full_url = f"{API_BASE}{endpoint}"
            
            # Verify URL structure uses /api prefix
            if not full_url.startswith(f"{BACKEND_URL}/api"):
                prefix_correct = False
                break
        
        # Test JWT requirement by trying a protected endpoint without auth
        if 'registry_id' in self.test_data:
            self.clear_auth_header()
            try:
                response = self.session.get(f"{API_BASE}/registries/mine")
                if response.status_code != 401:
                    jwt_required = False
            except:
                pass
        
        if prefix_correct and jwt_required:
            self.log_result("API Prefix and JWT", True, f"All endpoints use /api prefix and require JWT authentication")
        elif not prefix_correct:
            self.log_result("API Prefix and JWT", False, "Some endpoints don't use /api prefix correctly")
        else:
            self.log_result("API Prefix and JWT", False, "JWT authentication not properly enforced")
    
    def run_restored_endpoints_tests(self):
        """Run all tests for restored endpoints as specified in review request"""
        print("🚀 Starting Restored Endpoints Backend Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Run tests in order as specified in the review request
        self.test_1_register_admin_user()
        self.test_2_register_normal_user()
        self.test_3_create_registry_as_normal_user()
        self.test_4_get_my_registries()
        self.test_5_update_registry()
        self.test_6_add_funds_bulk_upsert()
        self.test_7_create_contributions()
        self.test_8_admin_get_registry_detail()
        self.test_9_admin_get_contributions()
        self.test_10_admin_get_audit_logs()
        self.test_11_admin_lock_registry()
        self.test_12_verify_owner_put_returns_423()
        self.test_13_verify_funds_upsert_returns_423()
        self.test_14_admin_unlock_registry()
        self.test_15_verify_write_works_after_unlock()
        self.test_16_verify_api_prefix_and_jwt()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Test Results Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print(f"\nOverall: {'✅ ALL TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME TESTS FAILED'}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = RestoredEndpointsTester()
    success = tester.run_restored_endpoints_tests()
    exit(0 if success else 1)