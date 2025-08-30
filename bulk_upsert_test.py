#!/usr/bin/env python3
"""
Test bulk upsert endpoint specifically for regression testing
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

print(f"Testing bulk upsert at: {API_BASE}")

class BulkUpsertTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_data = {}
    
    def setup_test_data(self):
        """Create user, registry and get auth token"""
        print("Setting up test data...")
        
        # Register user
        unique_id = str(uuid.uuid4())[:8]
        user_data = {
            "name": "Test User",
            "email": f"test.user.{unique_id}@example.com",
            "password": "TestPassword123!"
        }
        
        response = self.session.post(f"{API_BASE}/auth/register", json=user_data)
        if response.status_code == 201:
            data = response.json()
            self.test_data['user_token'] = data['access_token']
            self.test_data['user_id'] = data['user']['id']
            self.session.headers.update({'Authorization': f"Bearer {data['access_token']}"})
            print(f"✅ User registered: {data['user']['name']}")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            return False
        
        # Create registry
        registry_data = {
            "couple_names": "Sarah & Ahmed",
            "event_date": (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            "location": "Dubai, UAE",
            "currency": "AED",
            "slug": f"sarah-ahmed-{unique_id}",
            "theme": "modern"
        }
        
        response = self.session.post(f"{API_BASE}/registries", json=registry_data)
        if response.status_code == 201:
            data = response.json()
            self.test_data['registry_id'] = data['id']
            print(f"✅ Registry created: {data['slug']}")
            return True
        else:
            print(f"❌ Registry creation failed: {response.status_code}")
            return False
    
    def test_bulk_upsert_single_fund(self):
        """Test bulk upsert with single fund object"""
        print("\n=== Test: Bulk Upsert Single Fund ===")
        
        fund_data = {
            "title": "Honeymoon Suite",
            "description": "Luxury accommodation for our honeymoon",
            "goal": 3000.0,
            "category": "accommodation",
            "visible": True,
            "order": 1,
            "pinned": False
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert",
                json=fund_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 1:
                    fund = data[0]
                    if fund.get('title') == fund_data['title']:
                        self.test_data['fund_id_1'] = fund['id']
                        print(f"✅ Single fund bulk upsert: {fund['title']}")
                        return True
                    else:
                        print(f"❌ Wrong fund data: {fund}")
                else:
                    print(f"❌ Expected list with 1 item, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
            else:
                print(f"❌ Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        return False
    
    def test_bulk_upsert_multiple_funds(self):
        """Test bulk upsert with multiple funds array"""
        print("\n=== Test: Bulk Upsert Multiple Funds ===")
        
        funds_data = [
            {
                "title": "Flight Tickets",
                "description": "Business class flights to Maldives",
                "goal": 5000.0,
                "category": "travel",
                "visible": True,
                "order": 2,
                "pinned": True
            },
            {
                "title": "Spa & Wellness",
                "description": "Couples spa treatments and wellness activities",
                "goal": 1500.0,
                "category": "experiences",
                "visible": True,
                "order": 3,
                "pinned": False
            },
            {
                "title": "Fine Dining",
                "description": "Romantic dinners at exclusive restaurants",
                "goal": 2000.0,
                "category": "dining",
                "visible": True,
                "order": 4,
                "pinned": False
            }
        ]
        
        try:
            response = self.session.post(
                f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert",
                json=funds_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 3:
                    titles = [fund.get('title') for fund in data]
                    expected_titles = [fund['title'] for fund in funds_data]
                    
                    if all(title in titles for title in expected_titles):
                        print(f"✅ Multiple funds bulk upsert: {len(data)} funds created")
                        # Store fund IDs for update test
                        for fund in data:
                            if fund.get('title') == 'Flight Tickets':
                                self.test_data['fund_id_2'] = fund['id']
                        return True
                    else:
                        print(f"❌ Missing expected titles. Got: {titles}, Expected: {expected_titles}")
                else:
                    print(f"❌ Expected list with 3 items, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
            else:
                print(f"❌ Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        return False
    
    def test_bulk_upsert_update_existing(self):
        """Test bulk upsert to update existing fund"""
        print("\n=== Test: Bulk Upsert Update Existing Fund ===")
        
        if 'fund_id_2' not in self.test_data:
            print("❌ No fund ID available for update test")
            return False
        
        update_data = {
            "id": self.test_data['fund_id_2'],
            "title": "Premium Flight Tickets",
            "description": "First class flights to Maldives with lounge access",
            "goal": 8000.0,
            "category": "travel",
            "visible": True,
            "order": 2,
            "pinned": True
        }
        
        try:
            response = self.session.post(
                f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert",
                json=update_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 1:
                    fund = data[0]
                    if (fund.get('id') == self.test_data['fund_id_2'] and 
                        fund.get('title') == update_data['title'] and
                        fund.get('goal') == update_data['goal']):
                        print(f"✅ Fund update via bulk upsert: {fund['title']} - AED {fund['goal']}")
                        return True
                    else:
                        print(f"❌ Update not applied correctly: {fund}")
                else:
                    print(f"❌ Expected list with 1 item, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
            else:
                print(f"❌ Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        return False
    
    def test_bulk_upsert_mixed_operations(self):
        """Test bulk upsert with mixed create and update operations"""
        print("\n=== Test: Bulk Upsert Mixed Operations ===")
        
        if 'fund_id_1' not in self.test_data:
            print("❌ No fund ID available for mixed operations test")
            return False
        
        mixed_data = [
            {
                "id": self.test_data['fund_id_1'],
                "title": "Luxury Honeymoon Suite",
                "description": "Presidential suite with ocean view",
                "goal": 4500.0,
                "category": "accommodation",
                "visible": True,
                "order": 1,
                "pinned": True
            },
            {
                "title": "Adventure Activities",
                "description": "Scuba diving, snorkeling, and water sports",
                "goal": 1200.0,
                "category": "activities",
                "visible": True,
                "order": 5,
                "pinned": False
            }
        ]
        
        try:
            response = self.session.post(
                f"{API_BASE}/registries/{self.test_data['registry_id']}/funds/bulk_upsert",
                json=mixed_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 2:
                    # Check if first fund was updated
                    updated_fund = next((f for f in data if f.get('id') == self.test_data['fund_id_1']), None)
                    new_fund = next((f for f in data if f.get('title') == 'Adventure Activities'), None)
                    
                    if (updated_fund and updated_fund.get('title') == 'Luxury Honeymoon Suite' and
                        new_fund and new_fund.get('goal') == 1200.0):
                        print(f"✅ Mixed operations: 1 updated, 1 created")
                        return True
                    else:
                        print(f"❌ Mixed operations failed. Updated: {updated_fund is not None}, New: {new_fund is not None}")
                else:
                    print(f"❌ Expected list with 2 items, got: {type(data)} with {len(data) if isinstance(data, list) else 'N/A'} items")
            else:
                print(f"❌ Expected 200, got {response.status_code}: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
        
        return False
    
    def cleanup(self):
        """Clean up test data"""
        print("\n=== Cleanup ===")
        
        if 'registry_id' in self.test_data:
            try:
                response = self.session.delete(f"{API_BASE}/registries/{self.test_data['registry_id']}")
                if response.status_code == 200:
                    print("✅ Test registry deleted")
                else:
                    print(f"❌ Registry deletion failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Cleanup exception: {str(e)}")
    
    def run_tests(self):
        """Run all bulk upsert tests"""
        print("🚀 Starting Bulk Upsert Tests")
        print("=" * 60)
        
        if not self.setup_test_data():
            print("❌ Setup failed, aborting tests")
            return False
        
        results = []
        results.append(self.test_bulk_upsert_single_fund())
        results.append(self.test_bulk_upsert_multiple_funds())
        results.append(self.test_bulk_upsert_update_existing())
        results.append(self.test_bulk_upsert_mixed_operations())
        
        self.cleanup()
        
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 60)
        print("🏁 Bulk Upsert Test Results")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if passed == total:
            print("✅ ALL BULK UPSERT TESTS PASSED")
        else:
            print("❌ SOME BULK UPSERT TESTS FAILED")
        
        return passed == total

if __name__ == "__main__":
    tester = BulkUpsertTester()
    success = tester.run_tests()
    exit(0 if success else 1)