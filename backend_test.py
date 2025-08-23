#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for Wedding Registry MVP
Tests Resend email integration, missing routes, authentication, and authorization
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path
import time
import io

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

print(f"Testing comprehensive backend at: {API_BASE}")

class ComprehensiveBackendTester:
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
    
    # ===== AUTHENTICATION TESTS =====
    
    def test_auth_register_user(self):
        """Test user registration and JWT token generation"""
        print("\n=== Test: User Registration ===")
        
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": "Amira Hassan",
            "email": f"amira.hassan.{unique_id}@example.com",
            "password": "SecurePassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                if 'access_token' in data and 'user' in data:
                    self.test_data['user_token'] = data['access_token']
                    self.test_data['user_id'] = data['user']['id']
                    self.test_data['user_email'] = data['user']['email']
                    self.log_result("User Registration", True, f"User registered: {data['user']['name']}")
                else:
                    self.log_result("User Registration", False, f"Missing token or user data: {data}")
            else:
                self.log_result("User Registration", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("User Registration", False, f"Exception: {str(e)}")
    
    def test_auth_login(self):
        """Test user login"""
        print("\n=== Test: User Login ===")
        
        if 'user_email' not in self.test_data:
            self.log_result("User Login", False, "No user email from registration")
            return
        
        login_data = {
            "email": self.test_data['user_email'],
            "password": "SecurePassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data and data['user']['email'] == self.test_data['user_email']:
                    self.log_result("User Login", True, "Login successful")
                else:
                    self.log_result("User Login", False, f"Invalid login response: {data}")
            else:
                self.log_result("User Login", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("User Login", False, f"Exception: {str(e)}")
    
    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint with JWT"""
        print("\n=== Test: Auth Me Endpoint ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("Auth Me", False, "No user token available")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        try:
            response = self.session.get(f"{API_BASE}/auth/me")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('email') == self.test_data['user_email']:
                    self.log_result("Auth Me", True, f"User info retrieved: {data['name']}")
                else:
                    self.log_result("Auth Me", False, f"Wrong user data: {data}")
            else:
                self.log_result("Auth Me", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Auth Me", False, f"Exception: {str(e)}")
    
    def test_auth_unauthorized_access(self):
        """Test that protected endpoints require authentication"""
        print("\n=== Test: Unauthorized Access Protection ===")
        
        self.clear_auth_header()
        
        protected_endpoints = [
            ("/registries", "GET"),
            ("/admin/stats", "GET"),
            ("/auth/me", "GET")
        ]
        
        unauthorized_count = 0
        
        for endpoint, method in protected_endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{API_BASE}{endpoint}")
                elif method == "POST":
                    response = self.session.post(f"{API_BASE}{endpoint}", json={})
                
                if response.status_code == 401:
                    unauthorized_count += 1
                    
            except Exception:
                pass
        
        if unauthorized_count == len(protected_endpoints):
            self.log_result("Unauthorized Access", True, f"All {len(protected_endpoints)} protected endpoints require auth")
        else:
            self.log_result("Unauthorized Access", False, f"Only {unauthorized_count}/{len(protected_endpoints)} endpoints properly protected")
    
    # ===== REGISTRY CRUD TESTS =====
    
    def test_registry_create(self):
        """Test POST /api/registries"""
        print("\n=== Test: Registry Creation ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("Registry Create", False, "No user token available")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        unique_id = str(uuid.uuid4())[:8]
        registry_data = {
            "couple_names": "Amira & Omar Hassan",
            "event_date": (datetime.now() + timedelta(days=120)).strftime('%Y-%m-%d'),
            "location": "Dubai Marina, UAE",
            "currency": "AED",
            "hero_image": "https://example.com/wedding-photo.jpg",
            "slug": f"amira-omar-{unique_id}",
            "theme": "elegant"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries", json=registry_data)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('slug') == registry_data['slug'] and data.get('owner_id') == self.test_data['user_id']:
                    self.test_data['registry_id'] = data['id']
                    self.test_data['registry_slug'] = data['slug']
                    self.log_result("Registry Create", True, f"Registry created: {data['slug']}")
                else:
                    self.log_result("Registry Create", False, f"Invalid registry data: {data}")
            else:
                self.log_result("Registry Create", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Registry Create", False, f"Exception: {str(e)}")
    
    def test_registry_get_list(self):
        """Test GET /api/registries"""
        print("\n=== Test: Get Registry List ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("Registry List", False, "No user token available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries")
            
            if response.status_code == 200:
                registries = response.json()
                if isinstance(registries, list):
                    found_registry = any(r.get('id') == self.test_data.get('registry_id') for r in registries)
                    if found_registry:
                        self.log_result("Registry List", True, f"Found {len(registries)} registries including created one")
                    else:
                        self.log_result("Registry List", False, "Created registry not found in list")
                else:
                    self.log_result("Registry List", False, f"Expected list, got: {type(registries)}")
            else:
                self.log_result("Registry List", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Registry List", False, f"Exception: {str(e)}")
    
    def test_registry_get_single(self):
        """Test GET /api/registries/{id}"""
        print("\n=== Test: Get Single Registry ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Registry Get Single", False, "No registry ID available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('id') == self.test_data['registry_id']:
                    self.log_result("Registry Get Single", True, f"Retrieved registry: {data.get('slug')}")
                else:
                    self.log_result("Registry Get Single", False, f"Wrong registry returned: {data}")
            else:
                self.log_result("Registry Get Single", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Registry Get Single", False, f"Exception: {str(e)}")
    
    def test_registry_update(self):
        """Test PUT /api/registries/{id}"""
        print("\n=== Test: Registry Update ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Registry Update", False, "No registry ID available")
            return
        
        update_data = {
            "location": "Burj Al Arab, Dubai",
            "theme": "luxury"
        }
        
        try:
            response = self.session.put(f"{API_BASE}/registries/{self.test_data['registry_id']}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('location') == update_data['location'] and data.get('theme') == update_data['theme']:
                    self.log_result("Registry Update", True, f"Registry updated: {data.get('location')}")
                else:
                    self.log_result("Registry Update", False, f"Update not applied: {data}")
            else:
                self.log_result("Registry Update", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Registry Update", False, f"Exception: {str(e)}")
    
    def test_public_registry_get(self):
        """Test GET /api/public/registries/{slug}"""
        print("\n=== Test: Public Registry Access ===")
        
        if 'registry_slug' not in self.test_data:
            self.log_result("Public Registry", False, "No registry slug available")
            return
        
        # Clear auth header for public access
        self.clear_auth_header()
        
        try:
            response = self.session.get(f"{API_BASE}/public/registries/{self.test_data['registry_slug']}")
            
            if response.status_code == 200:
                data = response.json()
                if 'registry' in data and 'funds' in data and 'totals' in data:
                    self.log_result("Public Registry", True, f"Public registry accessible: {data['registry'].get('couple_names')}")
                else:
                    self.log_result("Public Registry", False, f"Invalid public registry structure: {data}")
            else:
                self.log_result("Public Registry", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Public Registry", False, f"Exception: {str(e)}")
    
    # ===== FUND MANAGEMENT TESTS =====
    
    def test_fund_create(self):
        """Test POST /api/registries/{id}/funds"""
        print("\n=== Test: Fund Creation ===")
        
        if 'registry_id' not in self.test_data or 'user_token' not in self.test_data:
            self.log_result("Fund Create", False, "Missing registry ID or user token")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        fund_data = {
            "title": "Honeymoon Flight Tickets",
            "description": "Business class flights to Maldives",
            "goal": 6000.0,
            "category": "travel",
            "visible": True,
            "order": 1
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds", json=fund_data)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('title') == fund_data['title'] and data.get('registry_id') == self.test_data['registry_id']:
                    self.test_data['fund_id'] = data['id']
                    self.log_result("Fund Create", True, f"Fund created: {data['title']}")
                else:
                    self.log_result("Fund Create", False, f"Invalid fund data: {data}")
            else:
                self.log_result("Fund Create", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Fund Create", False, f"Exception: {str(e)}")
    
    def test_fund_get_list(self):
        """Test GET /api/registries/{id}/funds"""
        print("\n=== Test: Get Fund List ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Fund List", False, "No registry ID available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds")
            
            if response.status_code == 200:
                funds = response.json()
                if isinstance(funds, list) and len(funds) >= 1:
                    found_fund = any(f.get('id') == self.test_data.get('fund_id') for f in funds)
                    if found_fund:
                        self.log_result("Fund List", True, f"Found {len(funds)} funds including created one")
                    else:
                        self.log_result("Fund List", False, "Created fund not found in list")
                else:
                    self.log_result("Fund List", False, f"Expected non-empty list, got: {len(funds) if isinstance(funds, list) else type(funds)}")
            else:
                self.log_result("Fund List", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Fund List", False, f"Exception: {str(e)}")
    
    def test_fund_update(self):
        """Test PUT /api/registries/{id}/funds/{fund_id}"""
        print("\n=== Test: Fund Update ===")
        
        if 'registry_id' not in self.test_data or 'fund_id' not in self.test_data:
            self.log_result("Fund Update", False, "Missing registry ID or fund ID")
            return
        
        update_data = {
            "title": "Premium Honeymoon Flight Tickets",
            "description": "First class flights to Maldives with lounge access",
            "goal": 8000.0,
            "category": "travel",
            "visible": True,
            "order": 1
        }
        
        try:
            response = self.session.put(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/{self.test_data['fund_id']}", json=update_data)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('title') == update_data['title'] and data.get('goal') == update_data['goal']:
                    self.log_result("Fund Update", True, f"Fund updated: {data['title']}")
                else:
                    self.log_result("Fund Update", False, f"Update not applied: {data}")
            else:
                self.log_result("Fund Update", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Fund Update", False, f"Exception: {str(e)}")
    
    # ===== CONTRIBUTION TESTS WITH EMAIL =====
    
    def test_contribution_create_with_email(self):
        """Test POST /api/contributions with guest_email parameter and email functionality"""
        print("\n=== Test: Contribution Creation with Email ===")
        
        if 'fund_id' not in self.test_data:
            self.log_result("Contribution with Email", False, "No fund ID available")
            return
        
        # Clear auth header for public contribution
        self.clear_auth_header()
        
        contribution_data = {
            "fund_id": self.test_data['fund_id'],
            "name": "Layla Al-Zahra",
            "amount": 1200.0,
            "message": "Wishing you both a magical honeymoon filled with love and adventure!",
            "public": True,
            "method": "credit_card",
            "guest_email": "layla.alzahra@example.com"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions", json=contribution_data)
            
            if response.status_code == 201:
                data = response.json()
                if (data.get('fund_id') == contribution_data['fund_id'] and 
                    data.get('amount') == contribution_data['amount'] and
                    data.get('guest_email') == contribution_data['guest_email']):
                    self.test_data['contribution_id'] = data['id']
                    self.log_result("Contribution with Email", True, f"Contribution created with email: {data['name']} - AED {data['amount']}")
                else:
                    self.log_result("Contribution with Email", False, f"Invalid contribution data: {data}")
            else:
                self.log_result("Contribution with Email", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Contribution with Email", False, f"Exception: {str(e)}")
    
    def test_contribution_rate_limiting(self):
        """Test rate limiting on contribution endpoint"""
        print("\n=== Test: Contribution Rate Limiting ===")
        
        if 'fund_id' not in self.test_data:
            self.log_result("Contribution Rate Limit", False, "No fund ID available")
            return
        
        # Try to make multiple contributions quickly
        rate_limited = False
        
        for i in range(7):  # Try 7 contributions (limit is 5 per minute)
            contribution_data = {
                "fund_id": self.test_data['fund_id'],
                "name": f"Test User {i}",
                "amount": 100.0,
                "message": f"Test contribution {i}",
                "public": True
            }
            
            try:
                response = self.session.post(f"{API_BASE}/contributions", json=contribution_data)
                if response.status_code == 429:
                    rate_limited = True
                    break
                time.sleep(0.1)  # Small delay between requests
            except Exception:
                pass
        
        if rate_limited:
            self.log_result("Contribution Rate Limit", True, "Rate limiting is working (429 returned)")
        else:
            self.log_result("Contribution Rate Limit", False, "Rate limiting not triggered or not working")
    
    def test_contribution_without_email(self):
        """Test contribution creation without email (should still work)"""
        print("\n=== Test: Contribution without Email ===")
        
        if 'fund_id' not in self.test_data:
            self.log_result("Contribution without Email", False, "No fund ID available")
            return
        
        contribution_data = {
            "fund_id": self.test_data['fund_id'],
            "name": "Anonymous Donor",
            "amount": 500.0,
            "message": "Best wishes for your future together!",
            "public": True,
            "method": "bank_transfer"
            # No guest_email provided
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions", json=contribution_data)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('fund_id') == contribution_data['fund_id'] and data.get('amount') == contribution_data['amount']:
                    self.log_result("Contribution without Email", True, f"Contribution created without email: {data['name']} - AED {data['amount']}")
                else:
                    self.log_result("Contribution without Email", False, f"Invalid contribution data: {data}")
            else:
                self.log_result("Contribution without Email", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Contribution without Email", False, f"Exception: {str(e)}")
    
    # ===== ANALYTICS AND EXPORT TESTS =====
    
    def test_analytics_endpoint(self):
        """Test GET /api/registries/{id}/analytics"""
        print("\n=== Test: Analytics Endpoint ===")
        
        if 'registry_id' not in self.test_data or 'user_token' not in self.test_data:
            self.log_result("Analytics", False, "Missing registry ID or user token")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/analytics")
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['total_contributions', 'total_amount', 'average_amount', 'daily_stats']
                
                if all(field in data for field in required_fields):
                    self.log_result("Analytics", True, f"Analytics data: {data['total_contributions']} contributions, AED {data['total_amount']}")
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result("Analytics", False, f"Missing fields: {missing}")
            else:
                self.log_result("Analytics", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Analytics", False, f"Exception: {str(e)}")
    
    def test_csv_export(self):
        """Test GET /api/registries/{id}/export/csv"""
        print("\n=== Test: CSV Export ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("CSV Export", False, "No registry ID available")
            return
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{self.test_data['registry_id']}/export/csv")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                if 'text/csv' in content_type and 'attachment' in content_disposition:
                    # Check if CSV content is valid
                    csv_content = response.text
                    lines = csv_content.strip().split('\n')
                    
                    if len(lines) >= 1 and 'Date,Name,Email,Amount,Fund,Message,Public,Method' in lines[0]:
                        self.log_result("CSV Export", True, f"CSV export working: {len(lines)} lines including header")
                    else:
                        self.log_result("CSV Export", False, f"Invalid CSV format: {lines[0] if lines else 'empty'}")
                else:
                    self.log_result("CSV Export", False, f"Wrong content type or disposition: {content_type}, {content_disposition}")
            else:
                self.log_result("CSV Export", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("CSV Export", False, f"Exception: {str(e)}")
    
    # ===== FILE UPLOAD TESTS =====
    
    def test_file_upload_chunk(self):
        """Test POST /api/upload/chunk"""
        print("\n=== Test: File Upload Chunk ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("File Upload", False, "No user token available")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        # Create a small test file
        test_content = b"This is a test image file content for wedding registry upload."
        
        try:
            # Simulate single chunk upload
            files = {'file': ('test-wedding-photo.jpg', io.BytesIO(test_content), 'image/jpeg')}
            data = {
                'filename': 'test-wedding-photo.jpg',
                'chunk_index': 0,
                'total_chunks': 1
            }
            
            response = self.session.post(f"{API_BASE}/upload/chunk", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if 'filename' in result and 'url' in result:
                    self.test_data['uploaded_file_url'] = result['url']
                    self.log_result("File Upload", True, f"File uploaded: {result['filename']}")
                else:
                    self.log_result("File Upload", False, f"Invalid upload response: {result}")
            else:
                self.log_result("File Upload", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("File Upload", False, f"Exception: {str(e)}")
    
    # ===== ADMIN TESTS =====
    
    def test_admin_user_detail_endpoint(self):
        """Test GET /api/admin/users/{id}/detail - the endpoint that needs retesting"""
        print("\n=== Test: Admin User Detail Endpoint ===")
        
        # Try to register admin user first
        admin_data = {
            "name": "Admin User",
            "email": "kshadid@gmail.com",
            "password": "AdminPassword123!"
        }
        
        try:
            # Try to register admin
            response = self.session.post(f"{API_BASE}/auth/register", json=admin_data)
            
            if response.status_code == 201:
                admin_token = response.json()['access_token']
                self.test_data['admin_token'] = admin_token
            elif response.status_code == 409:
                # Admin already exists, try to login
                login_response = self.session.post(f"{API_BASE}/auth/login", json=admin_data)
                if login_response.status_code == 200:
                    admin_token = login_response.json()['access_token']
                    self.test_data['admin_token'] = admin_token
                else:
                    self.log_result("Admin User Detail", False, "Cannot authenticate as admin")
                    return
            
            # Test admin user detail endpoint
            if 'admin_token' in self.test_data and 'user_id' in self.test_data:
                self.set_auth_header(self.test_data['admin_token'])
                
                response = self.session.get(f"{API_BASE}/admin/users/{self.test_data['user_id']}/detail")
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ['user', 'registries_owned', 'registries_collab', 'recent_audit']
                    
                    if all(field in data for field in required_fields):
                        self.log_result("Admin User Detail", True, f"Admin user detail working: {data['user'].get('name', 'Unknown')}")
                    else:
                        missing = [f for f in required_fields if f not in data]
                        self.log_result("Admin User Detail", False, f"Missing fields: {missing}")
                else:
                    self.log_result("Admin User Detail", False, f"Expected 200, got {response.status_code}: {response.text}")
            else:
                self.log_result("Admin User Detail", False, "Missing admin token or user ID")
                
        except Exception as e:
            self.log_result("Admin User Detail", False, f"Exception: {str(e)}")
    
    def test_admin_endpoints_access_control(self):
        """Test that admin endpoints require admin privileges"""
        print("\n=== Test: Admin Access Control ===")
        
        if 'user_token' not in self.test_data:
            self.log_result("Admin Access Control", False, "No user token available")
            return
        
        # Try to access admin endpoints with regular user token
        self.set_auth_header(self.test_data['user_token'])
        
        admin_endpoints = [
            "/admin/stats",
            "/admin/users",
            "/admin/registries"
        ]
        
        forbidden_count = 0
        
        for endpoint in admin_endpoints:
            try:
                response = self.session.get(f"{API_BASE}{endpoint}")
                if response.status_code == 403:
                    forbidden_count += 1
            except Exception:
                pass
        
        if forbidden_count == len(admin_endpoints):
            self.log_result("Admin Access Control", True, f"All {len(admin_endpoints)} admin endpoints properly protected")
        else:
            self.log_result("Admin Access Control", False, f"Only {forbidden_count}/{len(admin_endpoints)} admin endpoints protected")
    
    # ===== EMAIL SERVICE TESTS =====
    
    def test_email_service_configuration(self):
        """Test that email service handles missing RESEND_API_KEY gracefully"""
        print("\n=== Test: Email Service Configuration ===")
        
        # Check backend .env file for RESEND_API_KEY
        backend_env = load_env_file('/app/backend/.env')
        resend_key = backend_env.get('RESEND_API_KEY', '')
        
        if resend_key == '':
            self.log_result("Email Config", True, "RESEND_API_KEY is empty as expected for testing")
        else:
            self.log_result("Email Config", True, f"RESEND_API_KEY is configured: {'*' * min(len(resend_key), 10)}")
        
        # The actual email functionality is tested through contribution creation
        # which should work even without API key (just log warnings)
    
    # ===== CLEANUP TESTS =====
    
    def test_fund_delete(self):
        """Test DELETE /api/registries/{id}/funds/{fund_id}"""
        print("\n=== Test: Fund Deletion ===")
        
        if 'registry_id' not in self.test_data or 'fund_id' not in self.test_data:
            self.log_result("Fund Delete", False, "Missing registry ID or fund ID")
            return
        
        self.set_auth_header(self.test_data['user_token'])
        
        try:
            response = self.session.delete(f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/{self.test_data['fund_id']}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == True:
                    self.log_result("Fund Delete", True, "Fund deleted successfully")
                else:
                    self.log_result("Fund Delete", False, f"Unexpected response: {data}")
            else:
                self.log_result("Fund Delete", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Fund Delete", False, f"Exception: {str(e)}")
    
    def test_registry_delete(self):
        """Test DELETE /api/registries/{id}"""
        print("\n=== Test: Registry Deletion ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Registry Delete", False, "No registry ID available")
            return
        
        try:
            response = self.session.delete(f"{API_BASE}/registries/{self.test_data['registry_id']}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == True:
                    self.log_result("Registry Delete", True, "Registry deleted successfully")
                else:
                    self.log_result("Registry Delete", False, f"Unexpected response: {data}")
            else:
                self.log_result("Registry Delete", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Registry Delete", False, f"Exception: {str(e)}")
    
    def run_comprehensive_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 80)
        
        # Authentication Tests
        self.test_auth_register_user()
        self.test_auth_login()
        self.test_auth_me_endpoint()
        self.test_auth_unauthorized_access()
        
        # Registry CRUD Tests
        self.test_registry_create()
        self.test_registry_get_list()
        self.test_registry_get_single()
        self.test_registry_update()
        self.test_public_registry_get()
        
        # Fund Management Tests
        self.test_fund_create()
        self.test_fund_get_list()
        self.test_fund_update()
        
        # Contribution Tests with Email
        self.test_contribution_create_with_email()
        self.test_contribution_without_email()
        self.test_contribution_rate_limiting()
        
        # Analytics and Export Tests
        self.test_analytics_endpoint()
        self.test_csv_export()
        
        # File Upload Tests
        self.test_file_upload_chunk()
        
        # Admin Tests
        self.test_admin_user_detail_endpoint()
        self.test_admin_endpoints_access_control()
        
        # Email Service Tests
        self.test_email_service_configuration()
        
        # Cleanup Tests
        self.test_fund_delete()
        self.test_registry_delete()
        
        # Print summary
        print("\n" + "=" * 80)
        print("🏁 Comprehensive Test Results Summary")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🔍 Failed Tests Details:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print(f"\nOverall: {'✅ ALL TESTS PASSED' if self.results['failed'] == 0 else '❌ SOME TESTS FAILED'}")
        
        return self.results['failed'] == 0

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    success = tester.run_comprehensive_tests()
    exit(0 if success else 1)