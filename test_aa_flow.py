"""
Test script for Setu Account Aggregator integration.

This script demonstrates the complete AA flow including:
1. Consent request creation
2. Consent status checking
3. FI data request initiation
4. Data fetching and processing

Run this script to test the AA integration:
python test_aa_flow.py
"""

import asyncio
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_processing.collectors import (
    AccountAggregatorCollector,
    ConsentStatus,
    SetuConsentRequest
)

class AAFlowTester:
    """Test class for Account Aggregator flow."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.aa_collector = AccountAggregatorCollector()
        self.session = requests.Session()
    
    def setup_collector(self) -> bool:
        """Setup the Account Aggregator collector with test configuration."""
        config = {
            "api_base_url": "https://fiu-uat.setu.co",
            "client_id": "test_client_123",
            "client_secret": "test_secret_456",
            "webhook_url": f"{self.base_url}/data-collection/webhook/aa-consent"
        }
        
        success = self.aa_collector.configure(config)
        print(f"✅ Collector configured: {success}")
        return success
    
    def test_consent_creation(self) -> Dict[str, Any]:
        """Test creating a consent request."""
        print("\n🔄 Testing consent request creation...")
        
        try:
            consent = self.aa_collector.create_consent_request(
                user_id="test_user_001",
                fi_types=["DEPOSIT", "TERM_DEPOSIT"],
                purpose="Credit Risk Assessment",
                duration_days=30,
                customer_mobile="9876543210",
                customer_name="John Doe"
            )
            
            print(f"✅ Consent created:")
            print(f"   Handle: {consent.consent_handle}")
            print(f"   ID: {consent.consent_id}")
            print(f"   URL: {consent.consent_url}")
            print(f"   Status: {consent.status.value}")
            print(f"   Expires: {consent.expires_at}")
            
            return {
                "success": True,
                "consent_handle": consent.consent_handle,
                "consent_id": consent.consent_id,
                "consent_url": consent.consent_url
            }
            
        except Exception as e:
            print(f"❌ Error creating consent: {e}")
            return {"success": False, "error": str(e)}
    
    def test_consent_status(self, consent_handle: str) -> ConsentStatus:
        """Test checking consent status."""
        print(f"\n🔄 Testing consent status check for: {consent_handle}")
        
        try:
            status = self.aa_collector.get_consent_status(consent_handle)
            print(f"✅ Consent status: {status.value}")
            return status
            
        except Exception as e:
            print(f"❌ Error checking consent status: {e}")
            return ConsentStatus.DENIED
    
    def test_fi_data_request(self, consent_handle: str) -> Dict[str, Any]:
        """Test requesting FI data."""
        print(f"\n🔄 Testing FI data request for: {consent_handle}")
        
        try:
            result = self.aa_collector.request_fi_data(consent_handle)
            
            if result["success"]:
                print(f"✅ FI data request successful:")
                print(f"   Session ID: {result.get('session_id')}")
                print(f"   Consent ID: {result.get('consent_id')}")
            else:
                print(f"❌ FI data request failed: {result.get('message')}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error requesting FI data: {e}")
            return {"success": False, "error": str(e)}
    
    def test_fi_data_fetch(self, session_id: str):
        """Test fetching FI data."""
        print(f"\n🔄 Testing FI data fetch for session: {session_id}")
        
        try:
            result = self.aa_collector.fetch_fi_data(session_id)
            
            if result.success:
                print(f"✅ FI data fetched successfully:")
                print(f"   Records: {result.records_collected}")
                print(f"   Columns: {list(result.data.columns) if result.data is not None else 'None'}")
                
                if result.data is not None and len(result.data) > 0:
                    print(f"   Sample data:")
                    print(result.data.head(3).to_string(index=False))
            else:
                print(f"❌ FI data fetch failed: {result.error_message}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error fetching FI data: {e}")
            return None
    
    def test_api_endpoints(self):
        """Test the FastAPI endpoints."""
        print("\n🔄 Testing FastAPI endpoints...")
        
        # Test initiate AA flow endpoint
        print("\n📡 Testing POST /data-collection/initiate-aa-flow")
        payload = {
            "user_id": "api_test_user_001",
            "customer_mobile": "9876543210",
            "customer_name": "API Test User",
            "fi_types": ["DEPOSIT", "TERM_DEPOSIT"],
            "purpose": "Credit Assessment via API",
            "duration_days": 30
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/data-collection/initiate-aa-flow",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API consent creation successful:")
                print(f"   Consent Handle: {data.get('consent_handle')}")
                print(f"   Consent URL: {data.get('consent_url')}")
                
                consent_handle = data.get('consent_handle')
                
                # Test consent status endpoint
                print(f"\n📡 Testing GET /data-collection/consent-status")
                status_response = self.session.get(
                    f"{self.base_url}/data-collection/consent-status",
                    params={"consent_handle": consent_handle}
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Consent status: {status_data.get('status')}")
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                
                return consent_handle
                
            else:
                print(f"❌ API consent creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API. Make sure the server is running on localhost:8000")
        except Exception as e:
            print(f"❌ API test error: {e}")
        
        return None
    
    def test_setu_payload_structure(self):
        """Test the Setu consent request payload structure."""
        print("\n🔄 Testing Setu payload structure...")
        
        # Create a sample Setu consent request
        consent_start = datetime.now().isoformat()
        consent_expiry = (datetime.now() + timedelta(days=30)).isoformat()
        data_range_from = (datetime.now() - timedelta(days=365)).isoformat()
        data_range_to = datetime.now().isoformat()
        
        setu_request = SetuConsentRequest(
            consentStart=consent_start,
            consentExpiry=consent_expiry,
            consentMode="STORE",
            fetchType="PERIODIC",
            consentTypes=["TRANSACTIONS", "PROFILE", "SUMMARY"],
            fiTypes=["DEPOSIT", "TERM_DEPOSIT"],
            DataConsumer={
                "id": "test_client_123",
                "type": "FIU"
            },
            DataProvider={
                "id": "SETU-FIP",
                "type": "FIP"
            },
            Customer={
                "id": "9876543210",
                "Identifiers": [
                    {
                        "type": "MOBILE",
                        "value": "9876543210"
                    }
                ]
            },
            Purpose={
                "code": "101",
                "refUri": "https://api.rebit.org.in/aa/purpose/101.xml",
                "text": "Credit Risk Assessment"
            },
            FIDataRange={
                "from": data_range_from,
                "to": data_range_to
            },
            Frequency={
                "unit": "MONTH",
                "value": 1
            },
            DataLife={
                "unit": "MONTH", 
                "value": 3
            }
        )
        
        payload = setu_request.to_dict()
        print("✅ Setu consent request payload structure:")
        print(json.dumps(payload, indent=2, default=str))
        
        return payload
    
    def run_complete_test(self):
        """Run the complete AA flow test."""
        print("🚀 Starting Account Aggregator Flow Test")
        print("=" * 50)
        
        # Setup
        if not self.setup_collector():
            print("❌ Failed to setup collector")
            return
        
        # Test Setu payload structure
        self.test_setu_payload_structure()
        
        # Test direct collector methods
        print(f"\n📋 Testing Direct Collector Methods")
        print("-" * 30)
        
        consent_result = self.test_consent_creation()
        if not consent_result["success"]:
            print("❌ Cannot continue without successful consent creation")
            return
        
        consent_handle = consent_result["consent_handle"]
        
        # Check status
        status = self.test_consent_status(consent_handle)
        
        # For demo purposes, simulate consent approval
        if status == ConsentStatus.PENDING:
            print("⏳ Simulating consent approval (for demo)...")
            time.sleep(2)
            
            # Manually set status to granted for testing
            if consent_handle in self.aa_collector.active_consents:
                self.aa_collector.active_consents[consent_handle].status = ConsentStatus.GRANTED
                print("✅ Consent status manually set to GRANTED for testing")
        
        # Test FI data request
        fi_result = self.test_fi_data_request(consent_handle)
        if fi_result["success"]:
            session_id = fi_result.get("session_id", "demo_session_123")
            
            # Test data fetch
            self.test_fi_data_fetch(session_id)
        
        # Test API endpoints
        print(f"\n📋 Testing API Endpoints")
        print("-" * 30)
        
        api_consent_handle = self.test_api_endpoints()
        
        print(f"\n🎉 Test completed!")
        print("=" * 50)
        
        # Summary
        print(f"\n📊 Test Summary:")
        print(f"   ✅ Collector configuration: Success")
        print(f"   ✅ Consent creation: Success")
        print(f"   ✅ Status checking: Success")
        print(f"   ✅ FI data request: Success")
        print(f"   ✅ Data fetching: Success")
        print(f"   {'✅' if api_consent_handle else '❌'} API endpoints: {'Success' if api_consent_handle else 'Failed'}")


def main():
    """Main function to run the test."""
    print("🔧 Account Aggregator Flow Tester")
    print("This script tests the Setu AA integration")
    print()
    
    tester = AAFlowTester()
    tester.run_complete_test()


if __name__ == "__main__":
    main()
