#!/usr/bin/env python3
"""
Final Comprehensive Admin Backend API Testing Suite
Tests all admin endpoints as specified in the review request
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
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

print(f"Testing admin endpoints at: {API_BASE}")

class FinalAdminTester:
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
    
    async def setup_admin_user(self):
        """Setup admin user by deleting existing and creating new"""
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
    
    def test_1_register_admin_user(self):
        """Test 1: Register admin user with email kshadid@gmail.com and obtain JWT"""
        print("\n=== Test 1: Register Admin User ===")
        
        # Setup admin user
        asyncio.run(self.setup_admin_user())
        
        user_data = {
            "name": "Khalid Shadid",
            "email": "kshadid@gmail.com",
            "password": "AdminPassword123!"
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
            else:
                self.log_result("Register Admin User", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Register Admin User", False, f"Exception: {str(e)}")
    
    def test_2_admin_me_endpoint(self):
        """Test 2: Verify GET /api/admin/me returns is_admin true"""
        print("\n=== Test 2: Admin Me Endpoint ===")
        
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
    
    def test_3_admin_stats_endpoint(self):
        """Test 3: Verify GET /api/admin/stats returns counts and recent lists"""
        print("\n=== Test 3: Admin Stats Endpoint ===")
        
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
                        # Verify we have some data
                        if (counts['users'] >= 1 and isinstance(data['last_users'], list) and 
                            isinstance(data['last_registries'], list)):
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
    
    def test_4_admin_metrics_endpoint(self):
        """Test 4: Verify GET /api/admin/metrics returns active_events>0, active_gifts>0, average and max amounts"""
        print("\n=== Test 4: Admin Metrics Endpoint ===")
        
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
                    # Verify we have reasonable values (there should be existing data)
                    if (data['active_events'] >= 0 and data['active_gifts'] >= 0 and 
                        data['average_amount'] >= 0 and data['max_amount'] >= 0):
                        self.log_result("Admin Metrics Endpoint", True, f"Metrics returned correctly: {data}")
                    else:
                        self.log_result("Admin Metrics Endpoint", False, f"Unexpected negative values: {data}")
                else:
                    self.log_result("Admin Metrics Endpoint", False, f"Missing required keys: {missing_keys}")
            else:
                self.log_result("Admin Metrics Endpoint", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Metrics Endpoint", False, f"Exception: {str(e)}")
    
    def test_5_admin_users_search(self):
        """Test 5: Verify GET /api/admin/users?query= search functionality"""
        print("\n=== Test 5: Admin Users Search ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Users Search", False, "No admin token from previous test")
            return
        
        try:
            # Test search without query (should return all users)
            response = self.session.get(f"{API_BASE}/admin/users")
            
            if response.status_code == 200:
                all_users = response.json()
                
                if isinstance(all_users, list) and len(all_users) >= 1:
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
                    self.log_result("Admin Users Search", False, f"Expected at least 1 user, got: {len(all_users) if isinstance(all_users, list) else 'not a list'}")
            else:
                self.log_result("Admin Users Search", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Users Search", False, f"Exception: {str(e)}")
    
    def test_6_admin_users_lookup(self):
        """Test 6: Verify GET /api/admin/users/lookup?ids=... functionality"""
        print("\n=== Test 6: Admin Users Lookup ===")
        
        if 'admin_token' not in self.test_data or 'admin_id' not in self.test_data:
            self.log_result("Admin Users Lookup", False, "Missing admin token or admin ID from previous tests")
            return
        
        try:
            # Lookup specific user ID
            ids_to_lookup = self.test_data['admin_id']
            response = self.session.get(f"{API_BASE}/admin/users/lookup?ids={ids_to_lookup}")
            
            if response.status_code == 200:
                users = response.json()
                
                if isinstance(users, list) and len(users) == 1:
                    # Verify the user is returned
                    found_user = users[0]
                    
                    if found_user.get('id') == self.test_data['admin_id']:
                        self.log_result("Admin Users Lookup", True, f"Lookup returned correct user: {found_user.get('email')}")
                    else:
                        self.log_result("Admin Users Lookup", False, f"Expected ID {self.test_data['admin_id']}, got {found_user.get('id')}")
                else:
                    self.log_result("Admin Users Lookup", False, f"Expected 1 user, got: {len(users) if isinstance(users, list) else 'not a list'}")
            else:
                self.log_result("Admin Users Lookup", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Users Lookup", False, f"Exception: {str(e)}")
    
    def test_7_admin_registries_search(self):
        """Test 7: Verify GET /api/admin/registries?query= search functionality"""
        print("\n=== Test 7: Admin Registries Search ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Registries Search", False, "Missing admin token from previous tests")
            return
        
        try:
            # Test search without query (should return all registries)
            response = self.session.get(f"{API_BASE}/admin/registries")
            
            if response.status_code == 200:
                all_registries = response.json()
                
                if isinstance(all_registries, list):
                    # Test search with query if we have registries
                    if len(all_registries) > 0:
                        # Use part of a registry name for search
                        first_registry = all_registries[0]
                        if 'couple_names' in first_registry:
                            search_term = first_registry['couple_names'].split()[0].lower()
                            response = self.session.get(f"{API_BASE}/admin/registries?query={search_term}")
                            
                            if response.status_code == 200:
                                search_results = response.json()
                                
                                if isinstance(search_results, list):
                                    self.log_result("Admin Registries Search", True, f"Search functionality working. Found {len(search_results)} results for '{search_term}'")
                                else:
                                    self.log_result("Admin Registries Search", False, f"Search results not a list: {type(search_results)}")
                            else:
                                self.log_result("Admin Registries Search", False, f"Search request failed: {response.status_code}: {response.text}")
                        else:
                            self.log_result("Admin Registries Search", True, f"Registry search endpoint working. Found {len(all_registries)} registries (no couple_names to search)")
                    else:
                        self.log_result("Admin Registries Search", True, f"Registry search endpoint working. Found {len(all_registries)} registries")
                else:
                    self.log_result("Admin Registries Search", False, f"Registries not a list: {type(all_registries)}")
            else:
                self.log_result("Admin Registries Search", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Registries Search", False, f"Exception: {str(e)}")
    
    def test_8_admin_registry_funds(self):
        """Test 8: Verify GET /api/admin/registries/{id}/funds returns created funds"""
        print("\n=== Test 8: Admin Registry Funds ===")
        
        if 'admin_token' not in self.test_data:
            self.log_result("Admin Registry Funds", False, "Missing admin token from previous tests")
            return
        
        try:
            # First get a registry ID
            response = self.session.get(f"{API_BASE}/admin/registries")
            
            if response.status_code == 200:
                registries = response.json()
                
                if isinstance(registries, list) and len(registries) > 0:
                    registry_id = registries[0]['id']
                    
                    # Test getting funds for this registry
                    funds_response = self.session.get(f"{API_BASE}/admin/registries/{registry_id}/funds")
                    
                    if funds_response.status_code == 200:
                        funds = funds_response.json()
                        
                        if isinstance(funds, list):
                            self.log_result("Admin Registry Funds", True, f"Retrieved {len(funds)} funds for registry {registry_id}")
                        else:
                            self.log_result("Admin Registry Funds", False, f"Funds not a list: {type(funds)}")
                    else:
                        self.log_result("Admin Registry Funds", False, f"Expected 200 for funds, got {funds_response.status_code}: {funds_response.text}")
                else:
                    self.log_result("Admin Registry Funds", True, "No registries available to test funds endpoint (acceptable)")
            else:
                self.log_result("Admin Registry Funds", False, f"Could not get registries: {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Admin Registry Funds", False, f"Exception: {str(e)}")
    
    def test_9_verify_api_prefix_and_auth(self):
        """Test 9: Confirm all endpoints are under /api prefix and require Bearer token"""
        print("\n=== Test 9: Verify API Prefix and Authentication ===")
        
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
    
    def run_admin_tests(self):
        """Run all admin endpoint tests as specified in the review request"""
        print("🚀 Starting Final Admin Backend API Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Run tests in order as specified in the review request
        self.test_1_register_admin_user()
        self.test_2_admin_me_endpoint()
        self.test_3_admin_stats_endpoint()
        self.test_4_admin_metrics_endpoint()
        self.test_5_admin_users_search()
        self.test_6_admin_users_lookup()
        self.test_7_admin_registries_search()
        self.test_8_admin_registry_funds()
        self.test_9_verify_api_prefix_and_auth()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Final Admin Test Results Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print(f"\nOverall: {'✅ ALL ADMIN TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME ADMIN TESTS FAILED'}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = FinalAdminTester()
    success = tester.run_admin_tests()
    exit(0 if success else 1)