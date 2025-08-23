#!/usr/bin/env python3
"""
JWT Authentication Testing Suite for Honeymoon Registry MVP
Tests JWT auth endpoints and protected routes as specified in review request
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
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

print(f"Testing JWT Auth at: {API_BASE}")

class JWTAuthTester:
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
    
    def test_1_register_user(self):
        """Test 1: POST /api/auth/register with a new user; expect token + user"""
        print("\n=== Test 1: User Registration ===")
        
        # Generate unique email for this test run
        unique_id = str(uuid.uuid4())[:8]
        
        user_data = {
            "name": "Layla Al-Rashid",
            "email": f"layla.alrashid.{unique_id}@example.com",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response has token and user
                if ('access_token' in data and 'token_type' in data and 
                    'user' in data and data['token_type'] == 'bearer'):
                    
                    user = data['user']
                    if ('id' in user and 'name' in user and 'email' in user and
                        user['name'] == user_data['name'] and 
                        user['email'] == user_data['email']):
                        
                        self.test_data['access_token'] = data['access_token']
                        self.test_data['user'] = user
                        self.log_result("User Registration", True, f"User registered: {user['name']} ({user['email']})")
                    else:
                        self.log_result("User Registration", False, f"User data incomplete or incorrect: {user}")
                else:
                    self.log_result("User Registration", False, f"Missing token or user in response: {list(data.keys())}")
            else:
                self.log_result("User Registration", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
    
    def test_2_get_me_with_token(self):
        """Test 2: GET /api/auth/me with Bearer token; expect same user"""
        print("\n=== Test 2: Get Current User ===")
        
        if 'access_token' not in self.test_data:
            self.log_result("Get Current User", False, "No access_token from registration test")
            return
        
        headers = {
            'Authorization': f"Bearer {self.test_data['access_token']}"
        }
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                original_user = self.test_data['user']
                
                # Verify it's the same user
                if (user_data.get('id') == original_user.get('id') and
                    user_data.get('name') == original_user.get('name') and
                    user_data.get('email') == original_user.get('email')):
                    
                    self.log_result("Get Current User", True, f"Retrieved user: {user_data['name']} ({user_data['email']})")
                else:
                    self.log_result("Get Current User", False, f"User mismatch. Expected: {original_user}, Got: {user_data}")
            else:
                self.log_result("Get Current User", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Get Current User", False, f"Exception: {str(e)}")
    
    def test_3_create_registry_with_auth(self):
        """Test 3: POST /api/registries with Authorization header; expect 201 with owner_id"""
        print("\n=== Test 3: Create Registry with Auth ===")
        
        if 'access_token' not in self.test_data:
            self.log_result("Create Registry with Auth", False, "No access_token from registration test")
            return
        
        headers = {
            'Authorization': f"Bearer {self.test_data['access_token']}"
        }
        
        # Generate unique slug for this test run
        unique_id = str(uuid.uuid4())[:8]
        event_date = (datetime.now() + timedelta(days=200)).strftime('%Y-%m-%d')
        
        registry_data = {
            "couple_names": "Omar & Yasmin Al-Maktoum",
            "event_date": event_date,
            "location": "Dubai Marina, UAE",
            "currency": "AED",
            "hero_image": "https://example.com/dubai-marina-wedding.jpg",
            "slug": f"omar-yasmin-{unique_id}"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries", json=registry_data, headers=headers)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response has required fields including owner_id
                if ('id' in data and 'owner_id' in data and 
                    data.get('slug') == registry_data['slug'] and
                    data.get('owner_id') == self.test_data['user']['id']):
                    
                    self.test_data['registry_id'] = data['id']
                    self.test_data['registry_slug'] = data['slug']
                    self.log_result("Create Registry with Auth", True, f"Registry created with owner_id: {data['owner_id']}")
                else:
                    self.log_result("Create Registry with Auth", False, f"Missing id/owner_id or incorrect data: {data}")
            else:
                self.log_result("Create Registry with Auth", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create Registry with Auth", False, f"Exception: {str(e)}")
    
    def test_4_bulk_upsert_funds_with_auth(self):
        """Test 4: POST /api/registries/{id}/funds/bulk_upsert with Authorization; expect created>=1"""
        print("\n=== Test 4: Bulk Upsert Funds with Auth ===")
        
        if 'access_token' not in self.test_data or 'registry_id' not in self.test_data:
            self.log_result("Bulk Upsert Funds with Auth", False, "Missing access_token or registry_id from previous tests")
            return
        
        headers = {
            'Authorization': f"Bearer {self.test_data['access_token']}"
        }
        
        registry_id = self.test_data['registry_id']
        
        funds_data = {
            "funds": [
                {
                    "title": "Dubai Desert Safari Experience",
                    "description": "Private desert safari with camel riding and traditional dinner",
                    "goal": 3500.0,
                    "cover_url": "https://example.com/desert-safari.jpg",
                    "category": "experiences"
                },
                {
                    "title": "Burj Al Arab Spa Treatment",
                    "description": "Couples spa package at the world's most luxurious hotel",
                    "goal": 8000.0,
                    "cover_url": "https://example.com/burj-al-arab-spa.jpg",
                    "category": "wellness"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries/{registry_id}/funds/bulk_upsert", 
                                       json=funds_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify we have created count >= 1
                if 'created' in data and 'updated' in data:
                    created = data['created']
                    updated = data['updated']
                    
                    if created >= 1:
                        self.test_data['funds_created'] = created
                        self.test_data['funds_updated'] = updated
                        self.log_result("Bulk Upsert Funds with Auth", True, f"Created: {created}, Updated: {updated}")
                    else:
                        self.log_result("Bulk Upsert Funds with Auth", False, f"Expected created>=1, got created={created}")
                else:
                    self.log_result("Bulk Upsert Funds with Auth", False, f"Missing created/updated in response: {data}")
            else:
                self.log_result("Bulk Upsert Funds with Auth", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Bulk Upsert Funds with Auth", False, f"Exception: {str(e)}")
    
    def test_5_get_public_registry_no_auth(self):
        """Test 5: GET /api/registries/{slug}/public without auth; expect registry + funds"""
        print("\n=== Test 5: Get Public Registry (No Auth) ===")
        
        if 'registry_slug' not in self.test_data:
            self.log_result("Get Public Registry (No Auth)", False, "No registry_slug from previous tests")
            return
        
        slug = self.test_data['registry_slug']
        
        try:
            # Make request WITHOUT Authorization header
            response = self.session.get(f"{API_BASE}/registries/{slug}/public")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure: registry + funds + totals
                if 'registry' in data and 'funds' in data and 'totals' in data:
                    registry = data['registry']
                    funds = data['funds']
                    totals = data['totals']
                    
                    # Verify we have the funds we created
                    if isinstance(funds, list) and len(funds) >= 2:
                        self.test_data['public_funds'] = funds
                        self.test_data['initial_raised'] = totals.get('raised', 0)
                        self.log_result("Get Public Registry (No Auth)", True, 
                                      f"Registry: {registry['couple_names']}, Funds: {len(funds)}, Total raised: {totals.get('raised', 0)} AED")
                    else:
                        self.log_result("Get Public Registry (No Auth)", False, f"Expected at least 2 funds, got: {len(funds) if isinstance(funds, list) else 'not a list'}")
                else:
                    self.log_result("Get Public Registry (No Auth)", False, f"Missing registry/funds/totals in response: {list(data.keys())}")
            else:
                self.log_result("Get Public Registry (No Auth)", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Get Public Registry (No Auth)", False, f"Exception: {str(e)}")
    
    def test_6_create_contribution_no_auth(self):
        """Test 6: POST /api/contributions without auth; expect 201 and public registry raised increases"""
        print("\n=== Test 6: Create Contribution (No Auth) ===")
        
        if 'public_funds' not in self.test_data or not self.test_data['public_funds']:
            self.log_result("Create Contribution (No Auth)", False, "No public_funds from previous test")
            return
        
        # Use first fund for contribution
        fund_id = self.test_data['public_funds'][0]['id']
        
        contribution_data = {
            "fund_id": fund_id,
            "name": "Khalid Al-Mansoori",
            "amount": 750.0,
            "message": "Congratulations on your upcoming wedding! May your honeymoon be magical! 🌟",
            "public": True,
            "method": "bank_transfer"
        }
        
        try:
            # Make request WITHOUT Authorization header
            response = self.session.post(f"{API_BASE}/contributions", json=contribution_data)
            
            if response.status_code == 201:
                data = response.json()
                
                if 'id' in data and data.get('amount') == contribution_data['amount']:
                    self.test_data['contribution_id'] = data['id']
                    self.test_data['contribution_amount'] = data['amount']
                    self.log_result("Create Contribution (No Auth)", True, 
                                  f"Contribution created: {data['amount']} AED from {data.get('name', 'Anonymous')}")
                    
                    # Now verify the raised amount increased in public registry
                    self._verify_raised_amount_increased()
                else:
                    self.log_result("Create Contribution (No Auth)", False, f"Missing id or amount mismatch in response: {data}")
            else:
                self.log_result("Create Contribution (No Auth)", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create Contribution (No Auth)", False, f"Exception: {str(e)}")
    
    def _verify_raised_amount_increased(self):
        """Helper method to verify the raised amount increased after contribution"""
        print("\n=== Verifying Raised Amount Increased ===")
        
        if 'registry_slug' not in self.test_data or 'contribution_amount' not in self.test_data:
            self.log_result("Verify Raised Amount", False, "Missing registry_slug or contribution_amount")
            return
        
        slug = self.test_data['registry_slug']
        expected_increase = self.test_data['contribution_amount']
        initial_raised = self.test_data.get('initial_raised', 0)
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{slug}/public")
            
            if response.status_code == 200:
                data = response.json()
                current_raised = data.get('totals', {}).get('raised', 0)
                
                if current_raised >= initial_raised + expected_increase:
                    self.log_result("Verify Raised Amount", True, 
                                  f"Raised amount increased from {initial_raised} to {current_raised} AED (+{current_raised - initial_raised})")
                else:
                    self.log_result("Verify Raised Amount", False, 
                                  f"Expected raised >= {initial_raised + expected_increase}, got {current_raised}")
            else:
                self.log_result("Verify Raised Amount", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Verify Raised Amount", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all JWT auth tests in sequence"""
        print("🔐 Starting JWT Authentication Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Run tests in order as specified in review request
        self.test_1_register_user()
        self.test_2_get_me_with_token()
        self.test_3_create_registry_with_auth()
        self.test_4_bulk_upsert_funds_with_auth()
        self.test_5_get_public_registry_no_auth()
        self.test_6_create_contribution_no_auth()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 JWT Auth Test Results Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print(f"\nOverall: {'✅ ALL JWT AUTH TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME JWT AUTH TESTS FAILED'}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = JWTAuthTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)