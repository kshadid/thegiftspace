#!/usr/bin/env python3
"""
Backend API Testing Suite for Honeymoon Registry MVP
Tests all core backend endpoints with realistic data and JWT authentication
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

print(f"Testing backend at: {API_BASE}")

class BackendTester:
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
    
    def test_1_create_registry(self):
        """Test 1: Create a registry with realistic data"""
        print("\n=== Test 1: Create Registry ===")
        
        # Generate unique slug for this test run
        unique_id = str(uuid.uuid4())[:8]
        event_date = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        
        registry_data = {
            "couple_names": "Sarah & Ahmed Al-Mansouri",
            "event_date": event_date,
            "location": "Dubai, UAE",
            "currency": "AED",
            "hero_image": "https://example.com/dubai-wedding.jpg",
            "slug": f"sarah-ahmed-{unique_id}"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries", json=registry_data)
            
            if response.status_code == 201:
                data = response.json()
                
                # Verify response has required fields
                if 'id' in data and data.get('slug') == registry_data['slug']:
                    self.test_data['registry_id'] = data['id']
                    self.test_data['registry_slug'] = data['slug']
                    self.log_result("Create Registry", True, f"Registry created with ID: {data['id']}")
                else:
                    self.log_result("Create Registry", False, f"Missing id or slug mismatch in response: {data}")
            else:
                self.log_result("Create Registry", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create Registry", False, f"Exception: {str(e)}")
    
    def test_2_bulk_upsert_funds(self):
        """Test 2: Bulk upsert funds - one with ID, one without"""
        print("\n=== Test 2: Bulk Upsert Funds ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Bulk Upsert Funds", False, "No registry_id from previous test")
            return
        
        registry_id = self.test_data['registry_id']
        existing_fund_id = str(uuid.uuid4())
        
        funds_data = {
            "funds": [
                {
                    "id": existing_fund_id,  # Fund with ID (should be created first time, updated if run again)
                    "title": "Honeymoon Flight Tickets",
                    "description": "Business class flights to Maldives",
                    "goal": 15000.0,
                    "cover_url": "https://example.com/flights.jpg",
                    "category": "travel"
                },
                {
                    # Fund without ID (should always be created)
                    "title": "Luxury Resort Stay",
                    "description": "5-star overwater villa for 7 nights",
                    "goal": 25000.0,
                    "cover_url": "https://example.com/resort.jpg",
                    "category": "accommodation"
                }
            ]
        }
        
        try:
            response = self.session.post(f"{API_BASE}/registries/{registry_id}/funds/bulk_upsert", json=funds_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify we have created and updated counts
                if 'created' in data and 'updated' in data:
                    created = data['created']
                    updated = data['updated']
                    
                    if created >= 1 and updated >= 0:
                        self.test_data['fund_id_1'] = existing_fund_id
                        self.log_result("Bulk Upsert Funds", True, f"Created: {created}, Updated: {updated}")
                    else:
                        self.log_result("Bulk Upsert Funds", False, f"Expected created>=1 and updated>=0, got created={created}, updated={updated}")
                else:
                    self.log_result("Bulk Upsert Funds", False, f"Missing created/updated in response: {data}")
            else:
                self.log_result("Bulk Upsert Funds", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Bulk Upsert Funds", False, f"Exception: {str(e)}")
    
    def test_3_get_funds(self):
        """Test 3: Get funds to confirm bulk upsert worked"""
        print("\n=== Test 3: Get Registry Funds ===")
        
        if 'registry_id' not in self.test_data:
            self.log_result("Get Registry Funds", False, "No registry_id from previous test")
            return
        
        registry_id = self.test_data['registry_id']
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{registry_id}/funds")
            
            if response.status_code == 200:
                funds = response.json()
                
                if isinstance(funds, list) and len(funds) >= 2:
                    # Store fund IDs for contribution testing
                    self.test_data['fund_ids'] = [fund['id'] for fund in funds]
                    fund_titles = [fund['title'] for fund in funds]
                    self.log_result("Get Registry Funds", True, f"Found {len(funds)} funds: {fund_titles}")
                else:
                    self.log_result("Get Registry Funds", False, f"Expected at least 2 funds, got: {len(funds) if isinstance(funds, list) else 'not a list'}")
            else:
                self.log_result("Get Registry Funds", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Get Registry Funds", False, f"Exception: {str(e)}")
    
    def test_4_public_registry(self):
        """Test 4: Get public registry view"""
        print("\n=== Test 4: Public Registry View ===")
        
        if 'registry_slug' not in self.test_data:
            self.log_result("Public Registry View", False, "No registry_slug from previous test")
            return
        
        slug = self.test_data['registry_slug']
        
        try:
            response = self.session.get(f"{API_BASE}/registries/{slug}/public")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify structure
                if 'registry' in data and 'funds' in data and 'totals' in data:
                    registry = data['registry']
                    funds = data['funds']
                    totals = data['totals']
                    
                    # Check that funds have raised and progress fields
                    if isinstance(funds, list) and len(funds) > 0:
                        first_fund = funds[0]
                        if 'raised' in first_fund and 'progress' in first_fund:
                            self.test_data['initial_raised'] = totals.get('raised', 0)
                            self.log_result("Public Registry View", True, f"Registry: {registry['couple_names']}, Funds: {len(funds)}, Total raised: {totals.get('raised', 0)} AED")
                        else:
                            self.log_result("Public Registry View", False, "Funds missing raised/progress fields")
                    else:
                        self.log_result("Public Registry View", False, f"Expected funds list with items, got: {funds}")
                else:
                    self.log_result("Public Registry View", False, f"Missing registry/funds/totals in response: {list(data.keys())}")
            else:
                self.log_result("Public Registry View", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Public Registry View", False, f"Exception: {str(e)}")
    
    def test_5_create_contribution(self):
        """Test 5: Create a contribution to a fund"""
        print("\n=== Test 5: Create Contribution ===")
        
        if 'fund_ids' not in self.test_data or not self.test_data['fund_ids']:
            self.log_result("Create Contribution", False, "No fund_ids from previous test")
            return
        
        fund_id = self.test_data['fund_ids'][0]  # Use first fund
        
        contribution_data = {
            "fund_id": fund_id,
            "name": "Fatima Al-Zahra",
            "amount": 500.0,
            "message": "Wishing you both a wonderful honeymoon! 💕",
            "public": True,
            "method": "card"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/contributions", json=contribution_data)
            
            if response.status_code == 201:
                data = response.json()
                
                if 'id' in data and data.get('amount') == contribution_data['amount']:
                    self.test_data['contribution_id'] = data['id']
                    self.test_data['contribution_amount'] = data['amount']
                    self.log_result("Create Contribution", True, f"Contribution created: {data['amount']} AED from {data.get('name', 'Anonymous')}")
                else:
                    self.log_result("Create Contribution", False, f"Missing id or amount mismatch in response: {data}")
            else:
                self.log_result("Create Contribution", False, f"Expected 201, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Create Contribution", False, f"Exception: {str(e)}")
    
    def test_6_verify_contribution_impact(self):
        """Test 6: Verify contribution shows up in public registry with increased raised amount"""
        print("\n=== Test 6: Verify Contribution Impact ===")
        
        if 'registry_slug' not in self.test_data or 'contribution_amount' not in self.test_data:
            self.log_result("Verify Contribution Impact", False, "Missing registry_slug or contribution_amount from previous tests")
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
                    self.log_result("Verify Contribution Impact", True, f"Raised amount increased from {initial_raised} to {current_raised} AED")
                else:
                    self.log_result("Verify Contribution Impact", False, f"Expected raised >= {initial_raised + expected_increase}, got {current_raised}")
            else:
                self.log_result("Verify Contribution Impact", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Verify Contribution Impact", False, f"Exception: {str(e)}")
    
    def test_7_get_fund_contributions(self):
        """Test 7: Get contributions for a specific fund"""
        print("\n=== Test 7: Get Fund Contributions ===")
        
        if 'fund_ids' not in self.test_data or not self.test_data['fund_ids']:
            self.log_result("Get Fund Contributions", False, "No fund_ids from previous test")
            return
        
        fund_id = self.test_data['fund_ids'][0]  # Use first fund
        
        try:
            response = self.session.get(f"{API_BASE}/funds/{fund_id}/contributions")
            
            if response.status_code == 200:
                contributions = response.json()
                
                if isinstance(contributions, list) and len(contributions) >= 1:
                    # Find our contribution
                    our_contribution = None
                    for contrib in contributions:
                        if contrib.get('id') == self.test_data.get('contribution_id'):
                            our_contribution = contrib
                            break
                    
                    if our_contribution:
                        self.log_result("Get Fund Contributions", True, f"Found {len(contributions)} contributions including ours")
                    else:
                        self.log_result("Get Fund Contributions", False, f"Our contribution not found in {len(contributions)} contributions")
                else:
                    self.log_result("Get Fund Contributions", False, f"Expected at least 1 contribution, got: {len(contributions) if isinstance(contributions, list) else 'not a list'}")
            else:
                self.log_result("Get Fund Contributions", False, f"Expected 200, got {response.status_code}: {response.text}")
                
        except Exception as e:
            self.log_result("Get Fund Contributions", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting Backend API Tests")
        print(f"Backend URL: {API_BASE}")
        print("=" * 50)
        
        # Run tests in order
        self.test_1_create_registry()
        self.test_2_bulk_upsert_funds()
        self.test_3_get_funds()
        self.test_4_public_registry()
        self.test_5_create_contribution()
        self.test_6_verify_contribution_impact()
        self.test_7_get_fund_contributions()
        
        # Print summary
        print("\n" + "=" * 50)
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
    tester = BackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)