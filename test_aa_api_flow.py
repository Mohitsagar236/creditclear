"""
Test script for Account Aggregator Flow implementation.

This script demonstrates the complete AA flow including:
1. Consent request creation
2. Consent status monitoring
3. FI data request initiation
4. Financial data fetching
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30

class AAFlowTester:
    """Test class for Account Aggregator flow."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_health_check(self) -> bool:
        """Test API health check."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"✅ Health check: {response.status_code}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    def test_initiate_aa_flow(self, user_id: str = "test_user_123") -> Dict[str, Any]:
        """Test AA consent flow initiation."""
        print(f"\\n🚀 Starting AA flow for user: {user_id}")
        
        payload = {
            "user_id": user_id,
            "customer_mobile": "9876543210",
            "customer_name": "John Doe",
            "fi_types": ["DEPOSIT", "TERM_DEPOSIT"],
            "purpose": "Credit Assessment",
            "duration_days": 30
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/initiate-aa-flow",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Consent request created successfully")
                print(f"   Consent Handle: {data['consent_handle']}")
                print(f"   Consent ID: {data['consent_id']}")
                print(f"   Consent URL: {data['consent_url']}")
                print(f"   Status: {data['status']}")
                print(f"   Expires: {data['expires_at']}")
                return data
            else:
                print(f"❌ Failed to create consent: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception during consent creation: {e}")
            return {}
    
    def test_consent_status(self, consent_handle: str) -> str:
        """Test consent status checking."""
        print(f"\\n🔍 Checking consent status: {consent_handle}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/data-collection/consent-status",
                params={"consent_handle": consent_handle}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data['status']
                print(f"✅ Consent status: {status}")
                print(f"   User ID: {data['user_id']}")
                print(f"   Created: {data['created_at']}")
                print(f"   Expires: {data['expires_at']}")
                print(f"   Is Expired: {data['is_expired']}")
                return status
            else:
                print(f"❌ Failed to get consent status: {response.status_code}")
                print(f"   Error: {response.text}")
                return "ERROR"
                
        except Exception as e:
            print(f"❌ Exception during status check: {e}")
            return "ERROR"
    
    def test_request_fi_data(self, consent_handle: str) -> Dict[str, Any]:
        """Test FI data request."""
        print(f"\\n📊 Requesting FI data for consent: {consent_handle}")
        
        payload = {
            "consent_handle": consent_handle
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/request-fi-data",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FI data request initiated")
                print(f"   Session ID: {data['session_id']}")
                print(f"   Consent ID: {data['consent_id']}")
                print(f"   Estimated time: {data['estimated_time_minutes']} minutes")
                return data
            else:
                print(f"❌ Failed to request FI data: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception during FI data request: {e}")
            return {}
    
    def test_fetch_fi_data(self, session_id: str) -> Dict[str, Any]:
        """Test FI data fetching."""
        print(f"\\n💰 Fetching FI data for session: {session_id}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/data-collection/fetch-fi-data/{session_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ FI data fetched successfully")
                print(f"   Records count: {data['records_count']}")
                print(f"   Collection time: {data['collection_timestamp']}")
                
                # Show sample data
                if data['data'] and len(data['data']) > 0:
                    print(f"   Sample transaction:")
                    sample = data['data'][0]
                    for key, value in sample.items():
                        if key in ['account_id', 'transaction_date', 'amount', 'transaction_type']:
                            print(f"     {key}: {value}")
                
                return data
            else:
                print(f"❌ Failed to fetch FI data: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception during FI data fetch: {e}")
            return {}
    
    def test_collector_status(self) -> Dict[str, Any]:
        """Test collector status endpoint."""
        print(f"\\n📋 Checking collector status")
        
        try:
            response = self.session.get(f"{self.base_url}/data-collection/status")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Collector status retrieved")
                print(f"   Active consents: {data['active_consents']}")
                
                for collector_name, status in data['collectors'].items():
                    print(f"   {collector_name}:")
                    print(f"     Configured: {status['is_configured']}")
                    print(f"     Connection valid: {status['connection_valid']}")
                    print(f"     Last collection: {status['last_collection_time']}")
                
                return data
            else:
                print(f"❌ Failed to get collector status: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception during status check: {e}")
            return {}
    
    def test_device_data_submission(self, user_id: str = "test_user_123") -> Dict[str, Any]:
        """Test device data submission."""
        print(f"\\n📱 Testing device data submission for user: {user_id}")
        
        device_data = {
            "device_info": {
                "model": "iPhone 14",
                "os": "iOS",
                "os_version": "16.5",
                "screen_resolution": "1170x2532",
                "storage_gb": 128,
                "ram_gb": 6
            },
            "app_usage": {
                "installed_apps": ["WhatsApp", "Instagram", "Banking App", "Uber"],
                "screen_time_minutes": 480,
                "sessions_count": 25,
                "top_app": "Instagram",
                "apps_opened_today": 12
            },
            "network_behavior": {
                "data_usage_mb": 850,
                "wifi_usage_mb": 600,
                "cellular_usage_mb": 250,
                "wifi_networks": ["Home_WiFi", "Office_WiFi"],
                "data_saver": False
            },
            "location_data": {
                "locations": [
                    {"lat": 28.6139, "lng": 77.2090, "timestamp": "2024-01-15T10:00:00Z"},
                    {"lat": 28.5355, "lng": 77.3910, "timestamp": "2024-01-15T18:00:00Z"}
                ],
                "avg_accuracy": 15.0,
                "places_visited": 3,
                "distance_km": 25.5
            }
        }
        
        payload = {
            "user_id": user_id,
            "device_data": device_data
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/submit-device-data",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Device data submitted successfully")
                print(f"   Records processed: {data['records_processed']}")
                return data
            else:
                print(f"❌ Failed to submit device data: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Exception during device data submission: {e}")
            return {}
    
    def run_complete_aa_flow(self, user_id: str = "test_user_123") -> bool:
        """Run complete AA flow test."""
        print("=" * 80)
        print("🏦 ACCOUNT AGGREGATOR FLOW COMPLETE TEST")
        print("=" * 80)
        
        # Step 1: Health check
        if not self.test_health_check():
            return False
        
        # Step 2: Check collector status
        self.test_collector_status()
        
        # Step 3: Initiate AA flow
        consent_data = self.test_initiate_aa_flow(user_id)
        if not consent_data:
            return False
        
        consent_handle = consent_data['consent_handle']
        
        # Step 4: Monitor consent status (simulate approval)
        print(f"\\n⏳ Monitoring consent status (simulating user approval)...")
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            status = self.test_consent_status(consent_handle)
            
            if status == "GRANTED":
                break
            elif status in ["DENIED", "EXPIRED", "ERROR"]:
                print(f"❌ Consent failed with status: {status}")
                return False
            
            attempt += 1
            if attempt < max_attempts:
                print(f"   Waiting 3 seconds... (attempt {attempt}/{max_attempts})")
                time.sleep(3)
        
        if status != "GRANTED":
            print(f"❌ Consent not granted after {max_attempts} attempts")
            return False
        
        # Step 5: Request FI data
        fi_request_data = self.test_request_fi_data(consent_handle)
        if not fi_request_data:
            return False
        
        session_id = fi_request_data['session_id']
        
        # Step 6: Fetch FI data
        print(f"\\n⏳ Waiting 2 seconds before fetching data...")
        time.sleep(2)
        
        fi_data = self.test_fetch_fi_data(session_id)
        if not fi_data:
            return False
        
        # Step 7: Test device data submission
        self.test_device_data_submission(user_id)
        
        print("\\n" + "=" * 80)
        print("🎉 COMPLETE AA FLOW TEST SUCCESSFUL!")
        print("=" * 80)
        print(f"   User ID: {user_id}")
        print(f"   Consent Handle: {consent_handle}")
        print(f"   Session ID: {session_id}")
        print(f"   Financial records: {fi_data.get('records_count', 0)}")
        print("=" * 80)
        
        return True


def main():
    """Main test function."""
    print("🔧 Account Aggregator Flow API Test")
    print("=" * 50)
    
    # Create tester
    tester = AAFlowTester()
    
    # Run complete flow
    success = tester.run_complete_aa_flow("test_user_" + str(int(time.time())))
    
    if success:
        print("\\n✅ All tests passed!")
        exit(0)
    else:
        print("\\n❌ Some tests failed!")
        exit(1)


if __name__ == "__main__":
    main()
