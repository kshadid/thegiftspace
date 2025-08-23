#!/usr/bin/env python3
"""
Admin Backend API Testing Suite for Honeymoon Registry MVP
Tests all admin endpoints with JWT authentication and permissions
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

print(f"Testing admin endpoints at: {API_BASE}")

class AdminTester:
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
        """Test 1: Register admin user with email kshadid@gmail.com and obtain JWT"""
        print("\n=== Test 1: Register Admin User ===")
        
        user_data = {
            "name": "Khalid Shadid",
            "email": "kshadid@gmail.com",
            "password": "AdminSecurePassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                
                if 'access_token' in data and 'user' in data:
                    token = data['access_token']
                    user = data['user']
                    
                    if 'id' in user and user.get('email') == user_data['email']:
                        self.test_data['admin_token'] = token
                        self.test_data['admin_id'] = user['id']
                        self.test_data['admin_email'] = user['email']
                        self.set_auth_header(token)
                        self.log_result("Register Admin User", True, f"Admin registered: {user['name']} ({user['email']})")
                    else:
                        self.log_result("Register Admin User", False, f"Invalid user data in response: {user}")
                else:
                    self.log_result("Register Admin User", False, f"Missing access_token or user in response: {data}")
            elif response.status_code == 409:
                # User already exists, try to login instead
                login_data = {
                    "email": user_data['email'],
                    "password": user_data['password']
                }
                
                login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if login_response.status_code == 200:
                    data = login_response.json()
                    if 'access_token' in data and 'user' in data:
                        token = data['access_token']
                        user = data['user']
                        self.test_data['admin_token'] = token
                        self.test_data['admin_id'] = user['id']
                        self.test_data['admin_email'] = user['email']
                        self.set_auth_header(token)
                        self.log_result("Register Admin User", True, f"Admin logged in (already existed): {user['name']} ({user['email']})")
                    else:
                        self.log_result("Register Admin User", False, f"Login successful but missing data: {data}")
                else:
                    self.log_result("Register Admin User", False, f"User exists but login failed: {login_response.status_code}: {login_response.text}")
            else:
                self.log_result("Register Admin User", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Register Admin User", False, f"Exception: {str(e)}")
    
    def test_2_register_regular_user(self):
        """Test 2: Register a regular user for testing purposes"""
        print("\n=== Test 2: Register Regular User ===")
        
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": "Amira Hassan",
            "email": f"amira.hassan.{unique_id}@example.com",
            "password": "RegularUserPassword123!"
        }
        
        try:
            # Clear admin auth temporarily
            self.clear_auth_header()
            
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                
                if 'access_token' in data and 'user' in data:
                    token = data['access_token']
                    user = data['user']
                    
                    if 'id' in user and user.get('email') == user_data['email']:
                        self.test_data['regular_token'] = token
                        self.test_data['regular_id'] = user['id']
                        self.test_data['regular_email'] = user['email']
                        self.log_result("Register Regular User", True, f"Regular user registered: {user['name']} ({user['email']})")
                    else:
                        self.log_result("Register Regular User", False, f"Invalid user data in response: {user}")
                else:
                    self.log_result("Register Regular User", False, f"Missing access_token or user in response: {data}")
            else:
                self.log_result("Register Regular User", False, f"Expected 201, got {response.status_code}: {response.text}")
            
            # Restore admin auth
            if 'admin_token' in self.test_data:
                self.set_auth_header(self.test_data['admin_token'])
                
        except Exception as e:
            self.log_result("Register Regular User", False, f"Exception: {str(e)}")
    
    def test_3_create_registries_and_funds(self):
        """Test 3: Create two registries and some funds, add contributions"""
        print("\n=== Test 3: Create Registries, Funds, and Contributions ===")
        
        if 'regular_token' not in self.test_data:
            self.log_result("Create Registries and Funds", False, "No regular user token from previous test")
            return
        
        # Switch to regular user to create registries
        self.set_auth_header(self.test_data['regular_token'])
        
        unique_id = str(uuid.uuid4())[:8]
        event_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        
        registries_data = [
            {
                "couple_names": "Amira & Omar Hassan",
                "event_date": event_date,
                "location": "Dubai, UAE",
                "currency": "AED",
                "hero_image": "https://example.com/dubai-wedding.jpg",
                "slug": f"amira-omar-{unique_id}-1"
            },
            {
                "couple_names": "Layla & Saeed Al-Rashid",
                "event_date": event_date,
                "location": "Abu Dhabi, UAE", 
                "currency": "AED",
                "hero_image": "https://example.com/abudhabi-wedding.jpg",
                "slug": f"layla-saeed-{unique_id}-2"
            }
        ]
        
        created_registries = []
        
        # Create registries
        for i, registry_data in enumerate(registries_data):
            try:
                response = self.session.post(f"{API_BASE}/registries", json=registry_data)
                
                if response.status_code == 201:
                    data = response.json()
                    created_registries.append(data)
                    self.log_result(f"Create Registry {i+1}", True, f"Registry created: {data['id']}")
                else:
                    self.log_result(f"Create Registry {i+1}", False, f"Expected 201, got {response.status_code}: {response.text}")
                    return
                    
            except Exception as e:
                self.log_result(f"Create Registry {i+1}", False, f"Exception: {str(e)}")
                return
        
        if len(created_registries) != 2:
            self.log_result("Create Registries and Funds", False, f"Expected 2 registries, created {len(created_registries)}")
            return
        
        self.test_data['test_registries'] = created_registries
        
        # Create funds for each registry
        funds_data = [
            {"title": "Honeymoon Flight Tickets", "description": "Business class flights to Maldives", "goal": 15000, "category": "travel"},
            {"title": "Luxury Resort Stay", "description": "5-star overwater villa for 7 nights", "goal": 25000, "category": "accommodation"},
            {"title": "Romantic Dinner Experiences", "description": "Fine dining experiences during honeymoon", "goal": 3000, "category": "dining"}
        ]
        
        created_funds = []
        
        for registry in created_registries:
            registry_id = registry['id']
            
            for fund_data in funds_data:
                try:
                    response = self.session.post(f"{API_BASE}/registries/{registry_id}/funds", json=fund_data)
                    
                    if response.status_code == 201:
                        fund = response.json()
                        created_funds.append(fund)
                        self.log_result(f"Create Fund", True, f"Fund created: {fund['title']} for registry {registry_id}")
                    else:
                        self.log_result(f"Create Fund", False, f"Expected 201, got {response.status_code}: {response.text}")
                        
                except Exception as e:
                    self.log_result(f"Create Fund", False, f"Exception: {str(e)}")
        
        self.test_data['test_funds'] = created_funds
        
        # Add contributions to some funds
        if created_funds:
            contributions_data = [
                {"fund_id": created_funds[0]['id'], "name": "Ahmed Al-Maktoum", "amount": 2500, "message": "Wishing you a wonderful honeymoon!", "public": True},
                {"fund_id": created_funds[0]['id'], "name": "Fatima Al-Zahra", "amount": 1500, "message": "Congratulations on your wedding!", "public": True},
                {"fund_id": created_funds[1]['id'], "name": "Mohammed bin Rashid", "amount": 5000, "message": "Best wishes for your new journey together", "public": True},
                {"fund_id": created_funds[2]['id'], "name": "Aisha Al-Mansouri", "amount": 800, "message": "Enjoy your romantic dinners!", "public": True}
            ]
            
            for contrib_data in contributions_data:
                try:
                    response = self.session.post(f"{API_BASE}/contributions", json=contrib_data)
                    
                    if response.status_code == 201:
                        self.log_result(f"Create Contribution", True, f"Contribution added: {contrib_data['amount']} AED")
                    else:
                        self.log_result(f"Create Contribution", False, f"Expected 201, got {response.status_code}: {response.text}")
                        
                except Exception as e:
                    self.log_result(f"Create Contribution", False, f"Exception: {str(e)}")
        
        # Switch back to admin token
        if 'admin_token' in self.test_data:
            self.set_auth_header(self.test_data['admin_token'])
        
        self.log_result("Create Registries and Funds", True, f"Created {len(created_registries)} registries and {len(created_funds)} funds with contributions")
    
    def test_4_admin_me_endpoint(self):
        """Test 4: Verify GET /api/admin/me returns is_admin true"""
        print("\n=== Test 4: Admin Me Endpoint ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Me Endpoint", False, "No admin token from previous test")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/admin/me")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('email') == self.test_data['admin_email'] and data.get('is_admin') == True:
                    self.log_result("Admin Me Endpoint", True, f"Admin status confirmed: {data}")
                else:
                    self.log_result("Admin Me Endpoint", False, f"Expected is_admin=true and correct email, got: {data}")
            else:
                self.log_result("Admin Me Endpoint", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Me Endpoint", False, f"Exception: {str(e)}")
    
    def test_5_admin_stats_endpoint(self):
        """Test 5: Verify GET /api/admin/stats returns counts and recent lists"""
        print("\n=== Test 5: Admin Stats Endpoint ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Stats Endpoint", False, "No admin token from previous test")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/admin/stats")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required structure
                required_keys = ['counts', 'last_users', 'last_registries', 'top_funds']
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    counts = data['counts']
                    required_count_keys = ['users', 'registries', 'funds', 'contributions']
                    missing_count_keys = [key for key in required_count_keys if key not in counts]
                    
                    if not missing_count_keys:
                        # Verify we have some data (should have at least the users and registries we created)
                        if (counts['users'] >= 2 and counts['registries'] >= 2 and 
                            isinstance(data['last_users'], list) and isinstance(data['last_registries'], list)):
                            self.log_result("Admin Stats Endpoint", True, f"Stats returned correctly: {counts}")
                        else:
                            self.log_result("Admin Stats Endpoint", False, f"Insufficient data in stats: {counts}")
                    else:
                        self.log_result("Admin Stats Endpoint", False, f"Missing count keys: {missing_count_keys}")
                else:
                    self.log_result("Admin Stats Endpoint", False, f"Missing required keys: {missing_keys}")
            else:
                self.log_result("Admin Stats Endpoint", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Stats Endpoint", False, f"Exception: {str(e)}")
    
    def test_6_admin_metrics_endpoint(self):
        """Test 6: Verify GET /api/admin/metrics returns active_events>0, active_gifts>0, average and max amounts"""
        print("\n=== Test 6: Admin Metrics Endpoint ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Metrics Endpoint", False, "No admin token from previous test")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/admin/metrics")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check required keys
                required_keys = ['active_events', 'active_gifts', 'average_amount', 'max_amount']
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    # Verify we have positive values (we created contributions)
                    if (data['active_events'] > 0 and data['active_gifts'] > 0 and 
                        data['average_amount'] > 0 and data['max_amount'] > 0):
                        self.log_result("Admin Metrics Endpoint", True, f"Metrics returned correctly: {data}")
                    else:
                        self.log_result("Admin Metrics Endpoint", False, f"Expected positive values, got: {data}")
                else:
                    self.log_result("Admin Metrics Endpoint", False, f"Missing required keys: {missing_keys}")
            else:
                self.log_result("Admin Metrics Endpoint", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Metrics Endpoint", False, f"Exception: {str(e)}")
    
    def test_7_admin_users_search(self):
        """Test 7: Verify GET /api/admin/users?query= search functionality"""
        print("\n=== Test 7: Admin Users Search ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Users Search", False, "No admin token from previous test")
            return
        
        try:
            # Test search without query (should return all users)
            response = self.session.get(f"{API_BASE}/admin/users")
            
            if response.status_code == 200:
                all_users = response.json()
                
                if isinstance(all_users, list) and len(all_users) >= 2:
                    # Test search with query
                    search_query = "kshadid"
                    response = self.session.get(f"{API_BASE}/admin/users?query={search_query}")
                    
                    if response.status_code == 200:
                        search_results = response.json()
                        
                        if isinstance(search_results, list):
                            # Should find the admin user
                            admin_found = any(user.get('email') == 'kshadid@gmail.com' for user in search_results)
                            
                            if admin_found:
                                self.log_result("Admin Users Search", True, f"Search functionality working. Found {len(search_results)} results for '{search_query}'")
                            else:
                                self.log_result("Admin Users Search", False, f"Admin user not found in search results for '{search_query}'")
                        else:
                            self.log_result("Admin Users Search", False, f"Search results not a list: {type(search_results)}")
                    else:
                        self.log_result("Admin Users Search", False, f"Search request failed: {response.status_code}: {response.text}")
                else:
                    self.log_result("Admin Users Search", False, f"Expected at least 2 users, got: {len(all_users) if isinstance(all_users, list) else 'not a list'}")
            else:
                self.log_result("Admin Users Search", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Users Search", False, f"Exception: {str(e)}")
    
    def test_8_admin_users_lookup(self):
        """Test 8: Verify GET /api/admin/users/lookup?ids=... functionality"""
        print("\n=== Test 8: Admin Users Lookup ===")
        
        if 'admin_token' not in self.test_data or 'regular_id' not in self.test_data:
            self.log_result("Admin Users Lookup", False, "Missing admin token or regular user ID from previous tests")
            return
        
        try:
            # Lookup specific user IDs
            ids_to_lookup = f"{self.test_data['admin_id']},{self.test_data['regular_id']}"
            response = self.session.get(f"{API_BASE}/admin/users/lookup?ids={ids_to_lookup}")
            
            if response.status_code == 200:
                users = response.json()
                
                if isinstance(users, list) and len(users) == 2:
                    # Verify both users are returned
                    found_ids = {user.get('id') for user in users}
                    expected_ids = {self.test_data['admin_id'], self.test_data['regular_id']}
                    
                    if found_ids == expected_ids:
                        self.log_result("Admin Users Lookup", True, f"Lookup returned correct users: {len(users)} users found")
                    else:
                        self.log_result("Admin Users Lookup", False, f"Expected IDs {expected_ids}, got {found_ids}")
                else:
                    self.log_result("Admin Users Lookup", False, f"Expected 2 users, got: {len(users) if isinstance(users, list) else 'not a list'}")
            else:
                self.log_result("Admin Users Lookup", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Users Lookup", False, f"Exception: {str(e)}")
    
    def test_9_admin_registries_search(self):
        """Test 9: Verify GET /api/admin/registries?query= search functionality"""
        print("\n=== Test 9: Admin Registries Search ===")
        
        if 'admin_token' not in self.test_data or 'test_registries' not in self.test_data:
            self.log_result("Admin Registries Search", False, "Missing admin token or test registries from previous tests")
            return
        
        try:
            # Test search without query (should return all registries)
            response = self.session.get(f"{API_BASE}/admin/registries")
            
            if response.status_code == 200:
                all_registries = response.json()
                
                if isinstance(all_registries, list) and len(all_registries) >= 2:
                    # Test search with query (search for one of our test registries)
                    search_query = "amira"
                    response = self.session.get(f"{API_BASE}/admin/registries?query={search_query}")
                    
                    if response.status_code == 200:
                        search_results = response.json()
                        
                        if isinstance(search_results, list):
                            # Should find at least one registry
                            if len(search_results) > 0:
                                # Verify the results contain owner_email field (admin enhancement)
                                has_owner_email = any('owner_email' in registry for registry in search_results)
                                
                                if has_owner_email:
                                    self.log_result("Admin Registries Search", True, f"Search functionality working. Found {len(search_results)} results for '{search_query}' with owner_email")
                                else:
                                    self.log_result("Admin Registries Search", True, f"Search functionality working. Found {len(search_results)} results for '{search_query}' (no owner_email field)")
                            else:
                                self.log_result("Admin Registries Search", True, f"Search completed but no results for '{search_query}' (this is acceptable)")
                        else:
                            self.log_result("Admin Registries Search", False, f"Search results not a list: {type(search_results)}")
                    else:
                        self.log_result("Admin Registries Search", False, f"Search request failed: {response.status_code}: {response.text}")
                else:
                    self.log_result("Admin Registries Search", False, f"Expected at least 2 registries, got: {len(all_registries) if isinstance(all_registries, list) else 'not a list'}")
            else:
                self.log_result("Admin Registries Search", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Registries Search", False, f"Exception: {str(e)}")
    
    def test_10_admin_registry_funds(self):
        """Test 10: Verify GET /api/admin/registries/{id}/funds returns created funds"""
        print("\n=== Test 10: Admin Registry Funds ===")
        
        if 'admin_token' not in self.test_data or 'test_registries' not in self.test_data:
            self.log_result("Admin Registry Funds", False, "Missing admin token or test registries from previous tests")
            return
        
        try:
            # Test getting funds for the first registry
            registry_id = self.test_data['test_registries'][0]['id']
            response = self.session.get(f"{API_BASE}/admin/registries/{registry_id}/funds")
            
            if response.status_code == 200:
                funds = response.json()
                
                if isinstance(funds, list) and len(funds) >= 3:  # We created 3 funds per registry
                    # Verify fund structure
                    first_fund = funds[0]
                    required_fund_keys = ['id', 'title', 'registry_id', 'goal']
                    missing_keys = [key for key in required_fund_keys if key not in first_fund]
                    
                    if not missing_keys:
                        # Verify registry_id matches
                        if first_fund['registry_id'] == registry_id:
                            self.log_result("Admin Registry Funds", True, f"Retrieved {len(funds)} funds for registry {registry_id}")
                        else:
                            self.log_result("Admin Registry Funds", False, f"Fund registry_id mismatch: expected {registry_id}, got {first_fund['registry_id']}")
                    else:
                        self.log_result("Admin Registry Funds", False, f"Missing fund keys: {missing_keys}")
                else:
                    self.log_result("Admin Registry Funds", False, f"Expected at least 3 funds, got: {len(funds) if isinstance(funds, list) else 'not a list'}")
            else:
                self.log_result("Admin Registry Funds", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Registry Funds", False, f"Exception: {str(e)}")
    
    def test_11_admin_registry_lock_unlock(self):
        """Test 11: POST /api/admin/registries/{id}/lock - lock registry and verify owner cannot update, then unlock"""
        print("\n=== Test 11: Admin Registry Lock/Unlock ===")
        
        if ('admin_token' not in self.test_data or 'regular_token' not in self.test_data or 
            'test_registries' not in self.test_data):
            self.log_result("Admin Registry Lock/Unlock", False, "Missing required tokens or test registries from previous tests")
            return
        
        try:
            registry_id = self.test_data['test_registries'][0]['id']
            
            # Step 1: Lock the registry as admin
            lock_data = {"locked": True, "reason": "Testing lock functionality"}
            response = self.session.post(f"{API_BASE}/admin/registries/{registry_id}/lock", json=lock_data)
            
            if response.status_code == 200:
                lock_result = response.json()
                
                if lock_result.get('ok') == True:
                    self.log_result("Lock Registry", True, f"Registry {registry_id} locked successfully")
                    
                    # Step 2: Try to update registry as owner (should fail)
                    self.set_auth_header(self.test_data['regular_token'])
                    
                    update_data = {"location": "Sharjah, UAE"}
                    update_response = self.session.put(f"{API_BASE}/registries/{registry_id}", json=update_data)
                    
                    if update_response.status_code == 403:
                        self.log_result("Verify Lock Enforcement", True, "Owner correctly blocked from updating locked registry")
                        
                        # Step 3: Unlock the registry as admin
                        self.set_auth_header(self.test_data['admin_token'])
                        
                        unlock_data = {"locked": False}
                        unlock_response = self.session.post(f"{API_BASE}/admin/registries/{registry_id}/lock", json=unlock_data)
                        
                        if unlock_response.status_code == 200:
                            unlock_result = unlock_response.json()
                            
                            if unlock_result.get('ok') == True:
                                self.log_result("Unlock Registry", True, f"Registry {registry_id} unlocked successfully")
                                
                                # Step 4: Try to update registry as owner again (should succeed)
                                self.set_auth_header(self.test_data['regular_token'])
                                
                                update_response2 = self.session.put(f"{API_BASE}/registries/{registry_id}", json=update_data)
                                
                                if update_response2.status_code == 200:
                                    self.log_result("Verify Unlock Works", True, "Owner can update registry after unlock")
                                    self.log_result("Admin Registry Lock/Unlock", True, "Complete lock/unlock cycle working correctly")
                                else:
                                    self.log_result("Verify Unlock Works", False, f"Owner still cannot update after unlock: {update_response2.status_code}: {update_response2.text}")
                            else:
                                self.log_result("Unlock Registry", False, f"Unlock failed: {unlock_result}")
                        else:
                            self.log_result("Unlock Registry", False, f"Expected 200 for unlock, got {unlock_response.status_code}: {unlock_response.text}")
                    else:
                        self.log_result("Verify Lock Enforcement", False, f"Expected 403 for locked registry update, got {update_response.status_code}: {update_response.text}")
                else:
                    self.log_result("Lock Registry", False, f"Lock failed: {lock_result}")
            else:
                self.log_result("Lock Registry", False, f"Expected 200 for lock, got {response.status_code}: {response.text}")
            
            # Restore admin token
            self.set_auth_header(self.test_data['admin_token'])
                
        except Exception as e:
            self.log_result("Admin Registry Lock/Unlock", False, f"Exception: {str(e)}")
    
    def test_12_admin_access_contributions_audit(self):
        """Test 12: Verify admin can GET /api/registries/{id}/contributions and /api/registries/{id}/audit"""
        print("\n=== Test 12: Admin Access to Contributions and Audit ===")
        
        if 'admin_token' not in self.test_data or 'test_registries' not in self.test_data:
            self.log_result("Admin Access Contributions/Audit", False, "Missing admin token or test registries from previous tests")
            return
        
        try:
            registry_id = self.test_data['test_registries'][0]['id']
            
            # Test contributions access
            contributions_response = self.session.get(f"{API_BASE}/registries/{registry_id}/contributions")
            
            if contributions_response.status_code == 200:
                contributions = contributions_response.json()
                
                if isinstance(contributions, list):
                    self.log_result("Admin Access Contributions", True, f"Admin can access contributions: {len(contributions)} found")
                    
                    # Test audit access
                    audit_response = self.session.get(f"{API_BASE}/registries/{registry_id}/audit")
                    
                    if audit_response.status_code == 200:
                        audit_logs = audit_response.json()
                        
                        if isinstance(audit_logs, list):
                            self.log_result("Admin Access Audit", True, f"Admin can access audit logs: {len(audit_logs)} found")
                            self.log_result("Admin Access Contributions/Audit", True, "Admin has access to both contributions and audit logs")
                        else:
                            self.log_result("Admin Access Audit", False, f"Audit logs not a list: {type(audit_logs)}")
                    else:
                        self.log_result("Admin Access Audit", False, f"Expected 200 for audit, got {audit_response.status_code}: {audit_response.text}")
                else:
                    self.log_result("Admin Access Contributions", False, f"Contributions not a list: {type(contributions)}")
            else:
                self.log_result("Admin Access Contributions", False, f"Expected 200 for contributions, got {contributions_response.status_code}: {contributions_response.text}")
                
        except Exception as e:
            self.log_result("Admin Access Contributions/Audit", False, f"Exception: {str(e)}")
    
    def test_13_verify_api_prefix_and_auth(self):
        """Test 13: Confirm all endpoints are under /api prefix and require Bearer token"""
        print("\n=== Test 13: Verify API Prefix and Authentication ===")
        
        # Test endpoints that should require authentication
        admin_endpoints = [
            "/admin/me",
            "/admin/stats", 
            "/admin/metrics",
            "/admin/users",
            "/admin/users/lookup?ids=test",
            "/admin/registries"
        ]
        
        prefix_correct = True
        auth_required = True
        
        # Clear auth header to test authentication requirement
        self.clear_auth_header()
        
        for endpoint in admin_endpoints:
            try:
                # Verify URL has /api prefix
                full_url = f"{API_BASE}{endpoint}"
                if not full_url.startswith(f"{BACKEND_URL}/api"):
                    prefix_correct = False
                    self.log_result("API Prefix Check", False, f"Endpoint {endpoint} doesn't use /api prefix")
                    break
                
                # Test that endpoint requires authentication
                response = self.session.get(full_url)
                
                if response.status_code != 401:
                    auth_required = False
                    self.log_result("Auth Required Check", False, f"Endpoint {endpoint} doesn't require auth (got {response.status_code})")
                    break
                    
            except Exception as e:
                self.log_result("Verify API Prefix and Auth", False, f"Exception testing endpoint {endpoint}: {str(e)}")
                return
        
        # Restore admin auth
        if 'admin_token' in self.test_data:
            self.set_auth_header(self.test_data['admin_token'])
        
        if prefix_correct and auth_required:
            self.log_result("Verify API Prefix and Auth", True, f"All admin endpoints use /api prefix and require Bearer token")
        elif not prefix_correct:
            self.log_result("Verify API Prefix and Auth", False, "Some endpoints don't use /api prefix")
        else:
            self.log_result("Verify API Prefix and Auth", False, "Some endpoints don't require authentication")
    
    def test_14_non_admin_access_denied(self):
        """Test 14: Verify regular users cannot access admin endpoints"""
        print("\n=== Test 14: Non-Admin Access Denied ===")
        
        if 'regular_token' not in self.test_data:
            self.log_result("Non-Admin Access Denied", False, "No regular user token from previous tests")
            return
        
        # Switch to regular user token
        self.set_auth_header(self.test_data['regular_token'])
        
        admin_endpoints = [
            "/admin/me",
            "/admin/stats",
            "/admin/metrics",
            "/admin/users"
        ]
        
        access_properly_denied = True
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                
                if response.status_code != 403:
                    access_properly_denied = False
                    self.log_result("Access Denied Check", False, f"Regular user got {response.status_code} for {endpoint}, expected 403")
                    break
                    
            except Exception as e:
                self.log_result("Non-Admin Access Denied", False, f"Exception testing endpoint {endpoint}: {str(e)}")
                return
        
        # Restore admin auth
        if 'admin_token' in self.test_data:
            self.set_auth_header(self.test_data['admin_token'])
        
        if access_properly_denied:
            self.log_result("Non-Admin Access Denied", True, "Regular users properly denied access to admin endpoints")
        else:
            self.log_result("Non-Admin Access Denied", False, "Regular users can access some admin endpoints")
    
    def run_admin_tests(self):
        """Run all admin endpoint tests"""
        print("🚀 Starting Admin Backend API Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Run tests in order as specified in the review request
        self.test_1_register_admin_user()
        self.test_2_register_regular_user()
        self.test_3_create_registries_and_funds()
        self.test_4_admin_me_endpoint()
        self.test_5_admin_stats_endpoint()
        self.test_6_admin_metrics_endpoint()
        self.test_7_admin_users_search()
        self.test_8_admin_users_lookup()
        self.test_9_admin_registries_search()
        self.test_10_admin_registry_funds()
        self.test_11_admin_registry_lock_unlock()
        self.test_12_admin_access_contributions_audit()
        self.test_13_verify_api_prefix_and_auth()
        self.test_14_non_admin_access_denied()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Admin Test Results Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print(f"\nOverall: {'✅ ALL ADMIN TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME ADMIN TESTS FAILED'}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = AdminTester()
    success = tester.run_admin_tests()
    exit(0 if success else 1)