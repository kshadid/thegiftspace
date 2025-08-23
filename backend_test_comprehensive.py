#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Suite for Honeymoon Registry MVP
Tests specific features: unique indexes, rate limiting, analytics, CSV export, visibility flags
"""

import requests
import json
import uuid
import time
import csv
import io
from datetime import datetime, timedelta
import os
from pathlib import Path

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

print(f"Testing backend at: {API_BASE}")

class ComprehensiveBackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
        self.auth_token = None
    
    def log_result(self, test_name, success, message=""):
        if success:
            self.results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def setup_auth(self):
        """Setup authentication by registering and logging in a test user"""
        print("\n=== Setup: Authentication ===")
        
        # Generate unique user data
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": "Test User",
            "email": f"testuser{unique_id}@example.com",
            "password": "testpassword123"
        }
        
        try:
            # Register user
            response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
            
            if response.status_code == 201:
                data = response.json()
                self.auth_token = data.get('access_token')
                self.test_data['user_id'] = data.get('user', {}).get('id')
                self.test_data['user_email'] = user_data['email']
                self.test_data['user_password'] = user_data['password']
                
                # Set auth header for future requests
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                self.log_result("Setup Auth", True, f"User registered and authenticated: {user_data['email']}")
                return True
            else:
                self.log_result("Setup Auth", False, f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_result("Setup Auth", False, f"Exception during auth setup: {str(e)}")
            return False
    
    def test_unique_indexes(self):
        """Test 1: Unique indexes - expect 409 for duplicate email and registry slug"""
        print("\n=== Test 1: Unique Indexes ===")
        
        # Test 1a: Duplicate email registration
        duplicate_user_data = {
            "name": "Another User",
            "email": self.test_data['user_email'],  # Same email as registered user
            "password": "anotherpassword123"
        }
        
        try:
            # Temporarily remove auth header for registration test
            temp_auth = self.session.headers.pop('Authorization', None)
            
            response = self.session.post(f"{API_BASE}/auth/register", json=duplicate_user_data)
            
            # Restore auth header
            if temp_auth:
                self.session.headers['Authorization'] = temp_auth
            
            if response.status_code == 409:
                self.log_result("Unique Index - Email", True, "Got 409 for duplicate email registration")
            else:
                self.log_result("Unique Index - Email", False, f"Expected 409, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Unique Index - Email", False, f"Exception: {str(e)}")
        
        # Test 1b: Create registry with unique slug first
        unique_id = str(uuid.uuid4())[:8]
        registry_data = {
            "couple_names": "Sarah & Ahmed Al-Mansouri",
            "event_date": (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            "location": "Dubai, UAE",
            "currency": "AED",
            "slug": f"sarah-ahmed-{unique_id}"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries", json=registry_data)
            
            if response.status_code == 201:
                data = response.json()
                self.test_data['registry_id'] = data['id']
                self.test_data['registry_slug'] = data['slug']
                
                # Now try to create another registry with the same slug
                duplicate_registry_data = {
                    "couple_names": "Another Couple",
                    "event_date": (datetime.now() + timedelta(days=200)).strftime('%Y-%m-%d'),
                    "location": "Abu Dhabi, UAE",
                    "currency": "AED",
                    "slug": registry_data['slug']  # Same slug
                }
                
                duplicate_response = self.session.post(f"{API_BASE}/registries", json=duplicate_registry_data)
                
                if duplicate_response.status_code == 409:
                    self.log_result("Unique Index - Registry Slug", True, "Got 409 for duplicate registry slug")
                else:
                    self.log_result("Unique Index - Registry Slug", False, f"Expected 409, got {duplicate_response.status_code}: {duplicate_response.text}")
            else:
                self.log_result("Unique Index - Registry Slug", False, f"Failed to create initial registry: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Unique Index - Registry Slug", False, f"Exception: {str(e)}")
    
    def test_rate_limiting(self):
        """Test 2: Rate limiting - hit /api/auth/login >20 req/min, expect 429"""
        print("\n=== Test 2: Rate Limiting ===")
        
        login_data = {
            "email": self.test_data['user_email'],
            "password": self.test_data['user_password']
        }
        
        # Temporarily remove auth header for login tests
        temp_auth = self.session.headers.pop('Authorization', None)
        
        try:
            rate_limit_hit = False
            
            # Make rapid login requests (more than 20)
            for i in range(25):
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if response.status_code == 429:
                    rate_limit_hit = True
                    self.log_result("Rate Limiting", True, f"Got 429 (rate limited) on request #{i+1}")
                    break
                elif response.status_code != 200:
                    # Some other error, but not rate limiting
                    continue
                
                # Small delay to avoid overwhelming the server
                time.sleep(0.1)
            
            if not rate_limit_hit:
                self.log_result("Rate Limiting", False, "Did not hit rate limit after 25 requests")
                
        except Exception as e:
            self.log_result("Rate Limiting", False, f"Exception: {str(e)}")
        finally:
            # Restore auth header
            if temp_auth:
                self.session.headers['Authorization'] = temp_auth
    
    def test_analytics_and_csv(self):
        """Test 3 & 4: Analytics and CSV export with contributions across two funds"""
        print("\n=== Test 3 & 4: Analytics and CSV Export ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Analytics Setup", False, "No registry_id from previous test")
            return
        
        registry_id = self.test_data['registry_id']
        
        # Step 1: Create two funds with different visibility
        funds_data = {
            "funds": [
                {
                    "title": "Honeymoon Flight Tickets",
                    "description": "Business class flights to Maldives",
                    "goal": 15000.0,
                    "visible": True
                },
                {
                    "title": "Luxury Resort Stay",
                    "description": "5-star overwater villa for 7 nights",
                    "goal": 25000.0,
                    "visible": False  # This fund should be hidden from public API
                }
            ]
        }
        
        try:
            # Create funds
            response = self.session.post(f"{API_BASE}/registries/{registry_id}/funds/bulk_upsert", json=funds_data)
            
            if response.status_code != 200:
                self.log_result("Analytics Setup", False, f"Failed to create funds: {response.status_code} - {response.text}")
                return
            
            # Get fund IDs
            funds_response = self.session.get(f"{API_BASE}/registries/{registry_id}/funds")
            if funds_response.status_code != 200:
                self.log_result("Analytics Setup", False, f"Failed to get funds: {funds_response.status_code}")
                return
            
            funds = funds_response.json()
            if len(funds) < 2:
                self.log_result("Analytics Setup", False, f"Expected at least 2 funds, got {len(funds)}")
                return
            
            fund_ids = [fund['id'] for fund in funds]
            self.test_data['fund_ids'] = fund_ids
            
            # Step 2: Create contributions across both funds
            contributions = [
                {"fund_id": fund_ids[0], "name": "Fatima Al-Zahra", "amount": 500.0, "message": "Congratulations!", "public": True, "method": "card"},
                {"fund_id": fund_ids[0], "name": "Omar Hassan", "amount": 750.0, "message": "Best wishes!", "public": True, "method": "bank"},
                {"fund_id": fund_ids[1], "name": "Aisha Mohammed", "amount": 1000.0, "message": "Have a wonderful trip!", "public": True, "method": "card"},
                {"fund_id": fund_ids[1], "name": "Khalid Al-Rashid", "amount": 300.0, "message": "Enjoy your honeymoon!", "public": False, "method": "cash"}
            ]
            
            # Remove auth temporarily for contributions (they don't require auth)
            temp_auth = self.session.headers.pop('Authorization', None)
            
            for contrib in contributions:
                contrib_response = self.session.post(f"{API_BASE}/contributions", json=contrib)
                if contrib_response.status_code != 201:
                    self.log_result("Analytics Setup", False, f"Failed to create contribution: {contrib_response.status_code}")
                    if temp_auth:
                        self.session.headers['Authorization'] = temp_auth
                    return
            
            # Restore auth
            if temp_auth:
                self.session.headers['Authorization'] = temp_auth
            
            # Step 3: Test Analytics endpoint
            analytics_response = self.session.get(f"{API_BASE}/registries/{registry_id}/analytics")
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                
                # Check required keys
                required_keys = ['total', 'count', 'average', 'by_fund', 'daily']
                missing_keys = [key for key in required_keys if key not in analytics_data]
                
                if not missing_keys:
                    total = analytics_data['total']
                    count = analytics_data['count']
                    average = analytics_data['average']
                    by_fund = analytics_data['by_fund']
                    daily = analytics_data['daily']
                    
                    # Verify data makes sense
                    expected_total = 2550.0  # Sum of all contributions
                    expected_count = 4
                    
                    if abs(total - expected_total) < 0.01 and count == expected_count:
                        self.log_result("Analytics", True, f"Analytics data correct: total={total}, count={count}, avg={average:.2f}")
                    else:
                        self.log_result("Analytics", False, f"Analytics data incorrect: expected total={expected_total}, count={expected_count}, got total={total}, count={count}")
                else:
                    self.log_result("Analytics", False, f"Missing required keys in analytics: {missing_keys}")
            else:
                self.log_result("Analytics", False, f"Analytics endpoint failed: {analytics_response.status_code} - {analytics_response.text}")
            
            # Step 4: Test CSV Export
            csv_response = self.session.get(f"{API_BASE}/registries/{registry_id}/contributions/export/csv")
            
            if csv_response.status_code == 200:
                content_type = csv_response.headers.get('content-type', '')
                
                if 'text/csv' in content_type:
                    csv_content = csv_response.text
                    
                    # Parse CSV to check headers
                    csv_reader = csv.reader(io.StringIO(csv_content))
                    headers = next(csv_reader, [])
                    
                    expected_headers = ["created_at", "fund_title", "amount", "name", "message", "method", "public"]
                    
                    if headers == expected_headers:
                        # Count rows (should be 4 contributions)
                        rows = list(csv_reader)
                        if len(rows) == 4:
                            self.log_result("CSV Export", True, f"CSV export correct: {len(rows)} rows with proper headers")
                        else:
                            self.log_result("CSV Export", False, f"Expected 4 CSV rows, got {len(rows)}")
                    else:
                        self.log_result("CSV Export", False, f"CSV headers incorrect. Expected: {expected_headers}, Got: {headers}")
                else:
                    self.log_result("CSV Export", False, f"Expected text/csv content-type, got: {content_type}")
            else:
                self.log_result("CSV Export", False, f"CSV export failed: {csv_response.status_code} - {csv_response.text}")
                
        except Exception as e:
            self.log_result("Analytics and CSV", False, f"Exception: {str(e)}")
    
    def test_visibility_flag(self):
        """Test 5: Visibility flag - confirm public API excludes invisible funds"""
        print("\n=== Test 5: Visibility Flag ===")
        
        if 'registry_slug' not in self.test_data:
            self.log_result("Visibility Flag", False, "No registry_slug from previous test")
            return
        
        slug = self.test_data['registry_slug']
        
        try:
            # Remove auth for public API call
            temp_auth = self.session.headers.pop('Authorization', None)
            
            response = self.session.get(f"{API_BASE}/registries/{slug}/public")
            
            # Restore auth
            if temp_auth:
                self.session.headers['Authorization'] = temp_auth
            
            if response.status_code == 200:
                data = response.json()
                funds = data.get('funds', [])
                
                # Should only show visible funds (we created one visible, one invisible)
                visible_funds = [f for f in funds if f.get('visible', True)]
                
                if len(visible_funds) == 1:
                    visible_fund = visible_funds[0]
                    if visible_fund.get('title') == "Honeymoon Flight Tickets":
                        self.log_result("Visibility Flag", True, f"Public API correctly shows only 1 visible fund: {visible_fund['title']}")
                    else:
                        self.log_result("Visibility Flag", False, f"Wrong visible fund shown: {visible_fund.get('title')}")
                else:
                    self.log_result("Visibility Flag", False, f"Expected 1 visible fund, got {len(visible_funds)}")
            else:
                self.log_result("Visibility Flag", False, f"Public registry call failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.log_result("Visibility Flag", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all comprehensive backend tests"""
        print("🚀 Starting Comprehensive Backend API Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 60)
        
        # Setup authentication first
        if not self.setup_auth():
            print("❌ Authentication setup failed. Cannot proceed with tests.")
            return False
        
        # Run tests in order
        self.test_unique_indexes()
        self.test_rate_limiting()
        self.test_analytics_and_csv()
        self.test_visibility_flag()
        
        # Print summary
        print("\n" + "=" * 60)
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
    success = tester.run_all_tests()
    exit(0 if success else 1)