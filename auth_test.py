#!/usr/bin/env python3
"""
Comprehensive Authentication System Testing Suite
Focuses on investigating authentication issues where users report being unable to login with created accounts
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import os
import time
import pymongo
from pymongo import MongoClient

# Load environment variables
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

# Get configuration
frontend_env = load_env_file('/app/frontend/.env')
backend_env = load_env_file('/app/backend/.env')

BACKEND_URL = frontend_env.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
API_BASE = f"{BACKEND_URL}/api"
MONGO_URL = backend_env.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = backend_env.get('DB_NAME', 'test_database')

print(f"🔐 Testing Authentication System at: {API_BASE}")
print(f"📊 Database: {MONGO_URL}/{DB_NAME}")

class AuthenticationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'critical_issues': []
        }
        
        # Connect to MongoDB for direct database verification
        try:
            self.mongo_client = MongoClient(MONGO_URL)
            self.db = self.mongo_client[DB_NAME]
            print("✅ Connected to MongoDB for direct verification")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            self.mongo_client = None
            self.db = None
    
    def log_result(self, test_name, success, message="", is_critical=False):
        if success:
            self.results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results['failed'] += 1
            error_msg = f"{test_name}: {message}"
            self.results['errors'].append(error_msg)
            if is_critical:
                self.results['critical_issues'].append(error_msg)
            print(f"❌ {test_name}: FAILED {message}")
    
    def verify_user_in_database(self, email):
        """Directly check if user exists in MongoDB"""
        if self.db is None:
            return None, "No database connection"
        
        try:
            user = self.db.users.find_one({"email": email.lower()})
            if user:
                return user, "User found in database"
            else:
                return None, "User not found in database"
        except Exception as e:
            return None, f"Database error: {str(e)}"
    
    def test_user_registration_comprehensive(self):
        """Test user registration with comprehensive verification"""
        print("\n=== 🔐 COMPREHENSIVE USER REGISTRATION TEST ===")
        
        unique_id = str(uuid.uuid4())[:8]
        test_users = [
            {
                "name": "Fatima Al-Zahra",
                "email": f"fatima.alzahra.{unique_id}@example.com",
                "password": "SecurePassword123!"
            },
            {
                "name": "Ahmed Hassan", 
                "email": f"AHMED.HASSAN.{unique_id}@EXAMPLE.COM",  # Test case sensitivity
                "password": "AnotherPassword456!"
            }
        ]
        
        for i, user_data in enumerate(test_users):
            print(f"\n--- Testing User {i+1}: {user_data['name']} ---")
            
            try:
                # 1. Register user
                response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
                
                if response.status_code == 201:
                    data = response.json()
                    
                    # Verify response structure
                    if 'access_token' in data and 'user' in data:
                        user_info = data['user']
                        token = data['access_token']
                        
                        # Store for later tests
                        if i == 0:  # Store first user for main tests
                            self.test_data['user_token'] = token
                            self.test_data['user_id'] = user_info['id']
                            self.test_data['user_email'] = user_info['email']
                            self.test_data['user_password'] = user_data['password']
                            self.test_data['user_name'] = user_info['name']
                        
                        # 2. Verify user in database
                        db_user, db_msg = self.verify_user_in_database(user_data['email'])
                        
                        if db_user:
                            # Check password hash exists and is not plain text
                            if 'password_hash' in db_user and db_user['password_hash'] != user_data['password']:
                                # Check email case handling
                                stored_email = db_user['email']
                                if stored_email == user_data['email'].lower():
                                    self.log_result(f"Registration User {i+1}", True, 
                                                  f"User registered and stored correctly. Email normalized to: {stored_email}")
                                else:
                                    self.log_result(f"Registration User {i+1}", False, 
                                                  f"Email case handling issue. Stored: {stored_email}, Expected: {user_data['email'].lower()}", 
                                                  is_critical=True)
                            else:
                                self.log_result(f"Registration User {i+1}", False, 
                                              "Password not properly hashed or missing", is_critical=True)
                        else:
                            self.log_result(f"Registration User {i+1}", False, 
                                          f"User not found in database: {db_msg}", is_critical=True)
                    else:
                        self.log_result(f"Registration User {i+1}", False, 
                                      f"Missing token or user data in response: {data}", is_critical=True)
                else:
                    self.log_result(f"Registration User {i+1}", False, 
                                  f"Registration failed with status {response.status_code}: {response.text}", 
                                  is_critical=True)
                    
            except Exception as e:
                self.log_result(f"Registration User {i+1}", False, f"Exception: {str(e)}", is_critical=True)
    
    def test_login_comprehensive(self):
        """Test login with various scenarios"""
        print("\n=== 🔑 COMPREHENSIVE LOGIN TESTING ===")
        
        if 'user_email' not in self.test_data or 'user_password' not in self.test_data:
            self.log_result("Login Tests", False, "No user credentials from registration", is_critical=True)
            return
        
        email = self.test_data['user_email']
        password = self.test_data['user_password']
        
        # Test scenarios
        login_scenarios = [
            {
                "name": "Correct Credentials",
                "email": email,
                "password": password,
                "should_succeed": True
            },
            {
                "name": "Wrong Password",
                "email": email,
                "password": "WrongPassword123!",
                "should_succeed": False
            },
            {
                "name": "Case Sensitive Email Test",
                "email": email.upper(),
                "password": password,
                "should_succeed": True  # Should work due to email normalization
            },
            {
                "name": "Non-existent User",
                "email": "nonexistent@example.com",
                "password": password,
                "should_succeed": False
            },
            {
                "name": "Empty Password",
                "email": email,
                "password": "",
                "should_succeed": False
            }
        ]
        
        for scenario in login_scenarios:
            print(f"\n--- Testing: {scenario['name']} ---")
            
            login_data = {
                "email": scenario['email'],
                "password": scenario['password']
            }
            
            try:
                response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                
                if scenario['should_succeed']:
                    if response.status_code == 200:
                        data = response.json()
                        if 'access_token' in data and 'user' in data:
                            # Verify user data matches
                            if data['user']['email'].lower() == email.lower():
                                self.log_result(f"Login - {scenario['name']}", True, 
                                              f"Login successful for {data['user']['name']}")
                                
                                # Store token for further tests if this is the main login
                                if scenario['name'] == "Correct Credentials":
                                    self.test_data['login_token'] = data['access_token']
                            else:
                                self.log_result(f"Login - {scenario['name']}", False, 
                                              f"Wrong user returned: {data['user']['email']}", is_critical=True)
                        else:
                            self.log_result(f"Login - {scenario['name']}", False, 
                                          f"Missing token or user in response: {data}", is_critical=True)
                    else:
                        self.log_result(f"Login - {scenario['name']}", False, 
                                      f"Login failed with status {response.status_code}: {response.text}", 
                                      is_critical=True)
                else:
                    # Should fail
                    if response.status_code == 401:
                        self.log_result(f"Login - {scenario['name']}", True, 
                                      "Correctly rejected invalid credentials")
                    else:
                        self.log_result(f"Login - {scenario['name']}", False, 
                                      f"Expected 401, got {response.status_code}: {response.text}")
                        
            except Exception as e:
                self.log_result(f"Login - {scenario['name']}", False, f"Exception: {str(e)}", is_critical=True)
    
    def test_password_verification_logic(self):
        """Test password verification by examining database directly"""
        print("\n=== 🔒 PASSWORD VERIFICATION LOGIC TEST ===")
        
        if self.db is None or 'user_email' not in self.test_data:
            self.log_result("Password Verification", False, "No database connection or user email")
            return
        
        try:
            # Get user from database
            user = self.db.users.find_one({"email": self.test_data['user_email'].lower()})
            
            if user:
                stored_hash = user.get('password_hash', '')
                original_password = self.test_data['user_password']
                
                # Check hash format (bcrypt hashes start with $2b$)
                if stored_hash.startswith('$2b$') or stored_hash.startswith('$2a$'):
                    self.log_result("Password Hash Format", True, "Password properly hashed with bcrypt")
                    
                    # Test that hash is not the plain password
                    if stored_hash != original_password:
                        self.log_result("Password Security", True, "Password is hashed, not stored in plain text")
                    else:
                        self.log_result("Password Security", False, "Password stored in plain text!", is_critical=True)
                        
                else:
                    self.log_result("Password Hash Format", False, 
                                  f"Invalid hash format: {stored_hash[:20]}...", is_critical=True)
            else:
                self.log_result("Password Verification", False, "User not found in database", is_critical=True)
                
        except Exception as e:
            self.log_result("Password Verification", False, f"Exception: {str(e)}", is_critical=True)
    
    def test_jwt_token_validation(self):
        """Test JWT token validation and /auth/me endpoint"""
        print("\n=== 🎫 JWT TOKEN VALIDATION TEST ===")
        
        # Test with valid token
        if 'login_token' in self.test_data:
            print("--- Testing Valid Token ---")
            
            headers = {'Authorization': f'Bearer {self.test_data["login_token"]}'}
            
            try:
                response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if (data.get('email', '').lower() == self.test_data['user_email'].lower() and 
                        data.get('name') == self.test_data['user_name']):
                        self.log_result("JWT Valid Token", True, f"Token validation successful for {data['name']}")
                    else:
                        self.log_result("JWT Valid Token", False, 
                                      f"Token returned wrong user data: {data}", is_critical=True)
                else:
                    self.log_result("JWT Valid Token", False, 
                                  f"Valid token rejected with status {response.status_code}: {response.text}", 
                                  is_critical=True)
                    
            except Exception as e:
                self.log_result("JWT Valid Token", False, f"Exception: {str(e)}", is_critical=True)
        
        # Test with invalid tokens
        invalid_token_tests = [
            ("No Token", {}),
            ("Invalid Bearer Format", {'Authorization': 'InvalidFormat token123'}),
            ("Invalid Token", {'Authorization': 'Bearer invalid.token.here'}),
            ("Expired Token", {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid'})
        ]
        
        for test_name, headers in invalid_token_tests:
            print(f"--- Testing: {test_name} ---")
            
            try:
                response = self.session.get(f"{API_BASE}/auth/me", headers=headers)
                
                if response.status_code == 401:
                    self.log_result(f"JWT {test_name}", True, "Correctly rejected invalid token")
                else:
                    self.log_result(f"JWT {test_name}", False, 
                                  f"Expected 401, got {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log_result(f"JWT {test_name}", False, f"Exception: {str(e)}")
    
    def test_protected_endpoints_access(self):
        """Test that protected endpoints require valid authentication"""
        print("\n=== 🛡️ PROTECTED ENDPOINTS ACCESS TEST ===")
        
        protected_endpoints = [
            ("/registries", "GET"),
            ("/registries", "POST"),
            ("/admin/stats", "GET"),
            ("/auth/me", "GET")
        ]
        
        # Test without token
        print("--- Testing Without Authentication ---")
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
            self.log_result("Protected Endpoints", True, 
                          f"All {len(protected_endpoints)} endpoints properly require authentication")
        else:
            self.log_result("Protected Endpoints", False, 
                          f"Only {unauthorized_count}/{len(protected_endpoints)} endpoints require auth", 
                          is_critical=True)
        
        # Test with valid token
        if 'login_token' in self.test_data:
            print("--- Testing With Valid Authentication ---")
            
            headers = {'Authorization': f'Bearer {self.test_data["login_token"]}'}
            accessible_count = 0
            
            for endpoint, method in protected_endpoints:
                try:
                    if method == "GET":
                        response = self.session.get(f"{API_BASE}{endpoint}", headers=headers)
                    elif method == "POST":
                        # Use minimal valid data for POST requests
                        if endpoint == "/registries":
                            test_data = {
                                "couple_names": "Test Couple",
                                "slug": f"test-{uuid.uuid4().hex[:8]}",
                                "currency": "AED"
                            }
                            response = self.session.post(f"{API_BASE}{endpoint}", json=test_data, headers=headers)
                        else:
                            response = self.session.post(f"{API_BASE}{endpoint}", json={}, headers=headers)
                    
                    # Accept 200, 201, or other success codes (not 401/403)
                    if response.status_code not in [401, 403]:
                        accessible_count += 1
                        
                except Exception:
                    pass
            
            if accessible_count == len(protected_endpoints):
                self.log_result("Authenticated Access", True, 
                              f"All {len(protected_endpoints)} endpoints accessible with valid token")
            else:
                self.log_result("Authenticated Access", False, 
                              f"Only {accessible_count}/{len(protected_endpoints)} endpoints accessible with valid token")
    
    def test_duplicate_registration(self):
        """Test that duplicate email registration is properly handled"""
        print("\n=== 👥 DUPLICATE REGISTRATION TEST ===")
        
        if 'user_email' not in self.test_data:
            self.log_result("Duplicate Registration", False, "No user email from previous registration")
            return
        
        duplicate_user_data = {
            "name": "Different Name",
            "email": self.test_data['user_email'],  # Same email
            "password": "DifferentPassword123!"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=duplicate_user_data)
            
            if response.status_code == 409:
                self.log_result("Duplicate Registration", True, "Duplicate email correctly rejected with 409")
            else:
                self.log_result("Duplicate Registration", False, 
                              f"Expected 409 for duplicate email, got {response.status_code}: {response.text}", 
                              is_critical=True)
                
        except Exception as e:
            self.log_result("Duplicate Registration", False, f"Exception: {str(e)}", is_critical=True)
    
    def test_registration_login_flow(self):
        """Test complete registration -> login flow with fresh user"""
        print("\n=== 🔄 COMPLETE REGISTRATION -> LOGIN FLOW TEST ===")
        
        unique_id = str(uuid.uuid4())[:8]
        flow_user = {
            "name": "Layla Al-Mansouri",
            "email": f"layla.almansouri.{unique_id}@example.com",
            "password": "FlowTestPassword123!"
        }
        
        try:
            # Step 1: Register
            print("--- Step 1: Registration ---")
            reg_response = self.session.post(f"{API_BASE}/auth/register", json=flow_user)
            
            if reg_response.status_code == 201:
                reg_data = reg_response.json()
                print(f"✅ Registration successful: {reg_data['user']['name']}")
                
                # Step 2: Verify in database
                print("--- Step 2: Database Verification ---")
                db_user, db_msg = self.verify_user_in_database(flow_user['email'])
                
                if db_user:
                    print(f"✅ User found in database: {db_msg}")
                    
                    # Step 3: Login with same credentials
                    print("--- Step 3: Login Test ---")
                    login_data = {
                        "email": flow_user['email'],
                        "password": flow_user['password']
                    }
                    
                    login_response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                    
                    if login_response.status_code == 200:
                        login_data_resp = login_response.json()
                        if login_data_resp['user']['email'].lower() == flow_user['email'].lower():
                            self.log_result("Registration->Login Flow", True, 
                                          "Complete flow successful: Register -> DB Storage -> Login")
                        else:
                            self.log_result("Registration->Login Flow", False, 
                                          "Login returned different user", is_critical=True)
                    else:
                        self.log_result("Registration->Login Flow", False, 
                                      f"Login failed after successful registration: {login_response.status_code} - {login_response.text}", 
                                      is_critical=True)
                else:
                    self.log_result("Registration->Login Flow", False, 
                                  f"User not stored in database: {db_msg}", is_critical=True)
            else:
                self.log_result("Registration->Login Flow", False, 
                              f"Registration failed: {reg_response.status_code} - {reg_response.text}", 
                              is_critical=True)
                
        except Exception as e:
            self.log_result("Registration->Login Flow", False, f"Exception: {str(e)}", is_critical=True)
    
    def test_common_authentication_issues(self):
        """Test for common authentication problems"""
        print("\n=== 🐛 COMMON AUTHENTICATION ISSUES TEST ===")
        
        # Test case sensitivity issues
        if 'user_email' in self.test_data and 'user_password' in self.test_data:
            print("--- Testing Email Case Sensitivity ---")
            
            case_variants = [
                self.test_data['user_email'].lower(),
                self.test_data['user_email'].upper(),
                self.test_data['user_email'].title()
            ]
            
            successful_logins = 0
            
            for email_variant in case_variants:
                login_data = {
                    "email": email_variant,
                    "password": self.test_data['user_password']
                }
                
                try:
                    response = self.session.post(f"{API_BASE}/auth/login", json=login_data)
                    if response.status_code == 200:
                        successful_logins += 1
                except Exception:
                    pass
            
            if successful_logins == len(case_variants):
                self.log_result("Email Case Sensitivity", True, 
                              "Email login works regardless of case (good normalization)")
            else:
                self.log_result("Email Case Sensitivity", False, 
                              f"Only {successful_logins}/{len(case_variants)} case variants work", 
                              is_critical=True)
        
        # Test database connection
        print("--- Testing Database Connection ---")
        if self.db:
            try:
                # Try to ping the database
                self.mongo_client.admin.command('ping')
                user_count = self.db.users.count_documents({})
                self.log_result("Database Connection", True, f"Database accessible, {user_count} users found")
            except Exception as e:
                self.log_result("Database Connection", False, f"Database connection issue: {str(e)}", is_critical=True)
        else:
            self.log_result("Database Connection", False, "No database connection established", is_critical=True)
    
    def run_comprehensive_auth_tests(self):
        """Run all authentication tests"""
        print("🔐 STARTING COMPREHENSIVE AUTHENTICATION TESTING")
        print("=" * 80)
        print("This test suite investigates authentication issues where users")
        print("report being unable to login with created accounts.")
        print("=" * 80)
        
        # Core authentication flow tests
        self.test_user_registration_comprehensive()
        self.test_login_comprehensive()
        self.test_password_verification_logic()
        self.test_jwt_token_validation()
        self.test_protected_endpoints_access()
        
        # Edge case and issue detection tests
        self.test_duplicate_registration()
        self.test_registration_login_flow()
        self.test_common_authentication_issues()
        
        # Print comprehensive summary
        print("\n" + "=" * 80)
        print("🏁 COMPREHENSIVE AUTHENTICATION TEST RESULTS")
        print("=" * 80)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL AUTHENTICATION ISSUES FOUND ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"  🔴 {issue}")
        
        if self.results['errors']:
            print(f"\n🔍 ALL FAILED TESTS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        # Provide diagnosis
        print(f"\n📋 AUTHENTICATION SYSTEM DIAGNOSIS:")
        if self.results['failed'] == 0:
            print("  ✅ Authentication system appears to be working correctly")
            print("  ✅ No issues found that would prevent user login")
        elif self.results['critical_issues']:
            print("  🚨 CRITICAL ISSUES DETECTED that could prevent user login:")
            print("  🔧 These issues need immediate attention")
        else:
            print("  ⚠️  Minor issues detected but core authentication should work")
        
        print(f"\nOverall Result: {'✅ AUTHENTICATION SYSTEM HEALTHY' if len(self.results['critical_issues']) == 0 else '🚨 CRITICAL AUTHENTICATION ISSUES FOUND'}")
        
        # Close database connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return len(self.results['critical_issues']) == 0

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_comprehensive_auth_tests()
    exit(0 if success else 1)