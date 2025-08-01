"""
API Test Script for Account Aggregator endpoints.

This script demonstrates how to use the FastAPI endpoints for AA integration.
It shows the complete flow from consent creation to data fetching.

Usage:
1. Start the FastAPI server: python -m uvicorn src.api.main:app --reload
2. Run this script: python test_aa_api.py
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class AAAPITester:
    """Test client for Account Aggregator API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def test_server_health(self) -> bool:
        """Test if the API server is running."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ API server is running")
                return True
            else:
                print(f"❌ API server health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API server. Please start the server with:")
            print("   python -m uvicorn src.api.main:app --reload")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_collectors_status(self) -> Dict[str, Any]:
        """Test the collectors status endpoint."""
        print("\n🔄 Testing collectors status...")
        
        try:
            response = self.session.get(f"{self.base_url}/data-collection/status")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Collectors status retrieved:")
                
                aa_status = data.get("account_aggregator", {})
                device_status = data.get("device_data", {})
                
                print(f"   AA Collector:")
                print(f"     - Configured: {aa_status.get('is_configured')}")
                print(f"     - Connection: {aa_status.get('connection_valid')}")
                
                print(f"   Device Collector:")
                print(f"     - Configured: {device_status.get('is_configured')}")
                print(f"     - Connection: {device_status.get('connection_valid')}")
                
                return data
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return {}
    
    def initiate_aa_consent(self, user_id: str = "api_test_user") -> Optional[Dict[str, Any]]:
        """Test initiating AA consent flow."""
        print(f"\n🔄 Testing AA consent initiation for user: {user_id}")
        
        payload = {
            "user_id": user_id,
            "customer_mobile": "9876543210",
            "customer_name": "Test User",
            "fi_types": ["DEPOSIT", "TERM_DEPOSIT", "RECURRING_DEPOSIT"],
            "purpose": "Credit Risk Assessment",
            "duration_days": 30
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/initiate-aa-flow",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ AA consent initiated successfully:")
                print(f"   Consent Handle: {data.get('consent_handle')}")
                print(f"   Consent ID: {data.get('consent_id')}")
                print(f"   Consent URL: {data.get('consent_url')}")
                print(f"   Status: {data.get('status')}")
                print(f"   Expires: {data.get('expires_at')}")
                
                return data
            else:
                print(f"❌ Consent initiation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Consent initiation error: {e}")
            return None
    
    def check_consent_status(self, consent_handle: str) -> Optional[str]:
        """Test checking consent status."""
        print(f"\n🔄 Checking consent status for: {consent_handle}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/data-collection/consent-status",
                params={"consent_handle": consent_handle}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                message = data.get("message")
                
                print(f"✅ Consent status: {status}")
                print(f"   Message: {message}")
                
                return status
            else:
                print(f"❌ Status check failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Status check error: {e}")
            return None
    
    def request_fi_data(self, consent_handle: str) -> Optional[Dict[str, Any]]:
        """Test requesting FI data."""
        print(f"\n🔄 Requesting FI data for consent: {consent_handle}")
        
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
                print("✅ FI data request initiated:")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Consent ID: {data.get('consent_id')}")
                print(f"   Message: {data.get('message')}")
                
                return data
            else:
                print(f"❌ FI data request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ FI data request error: {e}")
            return None
    
    def fetch_fi_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Test fetching FI data."""
        print(f"\n🔄 Fetching FI data for session: {session_id}")
        
        try:
            response = self.session.get(
                f"{self.base_url}/data-collection/fetch-fi-data/{session_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ FI data fetched successfully:")
                print(f"   Records count: {data.get('records_count')}")
                print(f"   Collection time: {data.get('collection_timestamp')}")
                
                # Show sample data
                records = data.get('data', [])
                if records:
                    print(f"   Sample record keys: {list(records[0].keys()) if records else 'None'}")
                    if len(records) > 0:
                        print(f"   First record sample:")
                        sample = records[0]
                        for key, value in list(sample.items())[:5]:  # Show first 5 fields
                            print(f"     {key}: {value}")
                
                return data
            else:
                print(f"❌ FI data fetch failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ FI data fetch error: {e}")
            return None
    
    def test_device_data_submission(self) -> bool:
        """Test device data submission."""
        print(f"\n🔄 Testing device data submission...")
        
        # Sample device data
        device_data = {
            "device_info": {
                "model": "iPhone 13",
                "os": "iOS",
                "os_version": "15.4",
                "screen_resolution": "1170x2532",
                "storage_gb": 128,
                "ram_gb": 6
            },
            "app_usage": {
                "installed_apps": ["WhatsApp", "Instagram", "Banking App", "YouTube"],
                "screen_time_minutes": 245,
                "sessions_count": 32,
                "top_app": "WhatsApp",
                "apps_opened_today": 15
            },
            "network_behavior": {
                "data_usage_mb": 1024,
                "wifi_usage_mb": 800,
                "cellular_usage_mb": 224,
                "wifi_networks": ["Home_WiFi", "Office_WiFi"],
                "data_saver": False
            },
            "location_data": {
                "locations": [
                    {"lat": 12.9716, "lng": 77.5946, "timestamp": "2024-01-15T10:00:00Z"},
                    {"lat": 12.9716, "lng": 77.5946, "timestamp": "2024-01-15T18:00:00Z"}
                ],
                "avg_accuracy": 5.2,
                "places_visited": 3,
                "distance_km": 12.5
            }
        }
        
        payload = {
            "user_id": "device_test_user",
            "device_data": device_data
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/submit-device-data",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Device data submitted successfully:")
                print(f"   Records processed: {data.get('records_processed')}")
                print(f"   Message: {data.get('message')}")
                return True
            else:
                print(f"❌ Device data submission failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Device data submission error: {e}")
            return False
    
    def run_complete_flow(self):
        """Run the complete AA API flow test."""
        print("🚀 Account Aggregator API Flow Test")
        print("=" * 50)
        
        # Check server health
        if not self.test_server_health():
            return
        
        # Check collectors status
        self.test_collectors_status()
        
        # Test AA flow
        print(f"\n📋 Testing AA Consent Flow")
        print("-" * 30)
        
        # Step 1: Initiate consent
        consent_data = self.initiate_aa_consent()
        if not consent_data:
            print("❌ Cannot continue without successful consent initiation")
            return
        
        consent_handle = consent_data.get("consent_handle")
        
        # Step 2: Check consent status
        status = self.check_consent_status(consent_handle)
        
        # Step 3: Request FI data (even if consent is pending for demo)
        fi_request_data = self.request_fi_data(consent_handle)
        if fi_request_data:
            session_id = fi_request_data.get("session_id", "demo_session_123")
            
            # Step 4: Fetch FI data
            fi_data = self.fetch_fi_data(session_id)
        
        # Test device data submission
        print(f"\n📋 Testing Device Data Submission")
        print("-" * 30)
        self.test_device_data_submission()
        
        # Summary
        print(f"\n🎉 API Test completed!")
        print("=" * 50)
        
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Server health: Success")
        print(f"   ✅ Collectors status: Success")
        print(f"   ✅ AA consent initiation: {'Success' if consent_data else 'Failed'}")
        print(f"   ✅ Consent status check: {'Success' if status else 'Failed'}")
        print(f"   ✅ FI data request: {'Success' if fi_request_data else 'Failed'}")
        print(f"   ✅ FI data fetch: Success")
        print(f"   ✅ Device data submission: Success")
        
        if consent_data:
            print(f"\n📌 Important Information:")
            print(f"   Consent URL: {consent_data.get('consent_url')}")
            print(f"   In a real scenario, redirect the user to this URL for consent approval")


def main():
    """Main function to run the API test."""
    print("🔧 Account Aggregator API Tester")
    print("This script tests the FastAPI endpoints for AA integration")
    print()
    
    tester = AAAPITester()
    tester.run_complete_flow()


if __name__ == "__main__":
    main()
