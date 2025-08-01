"""
Direct test script for Account Aggregator Collector implementation.

This script tests the AccountAggregatorCollector class directly without
requiring the FastAPI server to be running.
"""

import sys
import os
import time
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_processing.collectors import (
    AccountAggregatorCollector,
    DeviceDataCollector,
    ConsentStatus,
    DataSourceType
)

class AACollectorTester:
    """Test class for Account Aggregator collector."""
    
    def __init__(self):
        self.aa_collector = AccountAggregatorCollector()
        self.device_collector = DeviceDataCollector()
    
    def test_aa_collector_configuration(self):
        """Test AA collector configuration."""
        print("🔧 Testing AA Collector Configuration")
        print("-" * 50)
        
        # Test configuration
        config = {
            "api_base_url": "https://fiu-uat.setu.co",
            "client_id": "demo_client_id",
            "client_secret": "demo_client_secret",
            "webhook_url": "https://your-domain.com/webhook/aa-consent"
        }
        
        success = self.aa_collector.configure(config)
        print(f"✅ Configuration: {'Success' if success else 'Failed'}")
        
        # Test connection validation
        connection_valid = self.aa_collector.validate_connection()
        print(f"✅ Connection validation: {'Success' if connection_valid else 'Failed'}")
        
        return success and connection_valid
    
    def test_consent_creation(self, user_id: str = "test_user_123"):
        """Test consent request creation."""
        print(f"\\n📋 Testing Consent Creation for User: {user_id}")
        print("-" * 50)
        
        consent = self.aa_collector.create_consent_request(
            user_id=user_id,
            fi_types=["DEPOSIT", "TERM_DEPOSIT"],
            purpose="Credit Assessment",
            duration_days=30,
            customer_mobile="9876543210",
            customer_name="John Doe"
        )
        
        print(f"✅ Consent created:")
        print(f"   User ID: {consent.user_id}")
        print(f"   Consent Handle: {consent.consent_handle}")
        print(f"   Consent ID: {consent.consent_id}")
        print(f"   Consent URL: {consent.consent_url}")
        print(f"   Status: {consent.status.value}")
        print(f"   Purpose: {consent.purpose}")
        print(f"   Duration: {consent.duration_days} days")
        print(f"   Created: {consent.created_at}")
        print(f"   Expires: {consent.expires_at}")
        print(f"   FI Types: {consent.fi_types}")
        
        return consent
    
    def test_consent_status_monitoring(self, consent_handle: str):
        """Test consent status monitoring."""
        print(f"\\n🔍 Testing Consent Status Monitoring")
        print("-" * 50)
        
        max_attempts = 12  # 12 attempts = 36 seconds (enough for demo auto-approval)
        attempt = 0
        
        while attempt < max_attempts:
            status = self.aa_collector.get_consent_status(consent_handle)
            print(f"   Attempt {attempt + 1}: Status = {status.value}")
            
            if status == ConsentStatus.GRANTED:
                print(f"✅ Consent granted after {attempt + 1} attempts!")
                return True
            elif status in [ConsentStatus.DENIED, ConsentStatus.EXPIRED]:
                print(f"❌ Consent failed with status: {status.value}")
                return False
            
            attempt += 1
            if attempt < max_attempts:
                time.sleep(3)  # Wait 3 seconds between checks
        
        print(f"⏰ Consent status polling timeout after {max_attempts} attempts")
        return False
    
    def test_fi_data_request(self, consent_handle: str):
        """Test FI data request."""
        print(f"\\n📊 Testing FI Data Request")
        print("-" * 50)
        
        result = self.aa_collector.request_fi_data(consent_handle)
        
        if result["success"]:
            print(f"✅ FI data request successful:")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Consent ID: {result['consent_id']}")
            print(f"   Message: {result['message']}")
            return result["session_id"]
        else:
            print(f"❌ FI data request failed:")
            print(f"   Error: {result['error']}")
            print(f"   Message: {result['message']}")
            return None
    
    def test_fi_data_fetch(self, session_id: str):
        """Test FI data fetching."""
        print(f"\\n💰 Testing FI Data Fetch")
        print("-" * 50)
        
        result = self.aa_collector.fetch_fi_data(session_id)
        
        if result.success:
            print(f"✅ FI data fetch successful:")
            print(f"   Records collected: {result.records_collected}")
            print(f"   Collection timestamp: {result.collection_timestamp}")
            print(f"   Data source: {result.metadata.get('data_source')}")
            print(f"   Session ID: {result.metadata.get('session_id')}")
            
            # Show sample data structure
            if result.data is not None and not result.data.empty:
                print(f"   DataFrame shape: {result.data.shape}")
                print(f"   DataFrame columns: {list(result.data.columns)}")
                
                # Show first few rows
                print(f"\\n   Sample data:")
                sample_data = result.data.head(3)
                for idx, row in sample_data.iterrows():
                    print(f"   Row {idx + 1}:")
                    for col in ['account_id', 'transaction_date', 'amount', 'transaction_type']:
                        if col in row:
                            print(f"     {col}: {row[col]}")
            
            return result
        else:
            print(f"❌ FI data fetch failed:")
            print(f"   Error: {result.error_message}")
            return None
    
    def test_device_data_collection(self, user_id: str = "test_user_123"):
        """Test device data collection."""
        print(f"\\n📱 Testing Device Data Collection")
        print("-" * 50)
        
        # Configure device collector
        device_config = {
            "validation_rules": {},
            "privacy_settings": {"anonymize_location": True}
        }
        self.device_collector.configure(device_config)
        
        # Sample device data
        device_data = {
            "user_id": user_id,
            "device_info": {
                "model": "Samsung Galaxy S23",
                "os": "Android",
                "os_version": "13",
                "screen_resolution": "1080x2340",
                "storage_gb": 256,
                "ram_gb": 8
            },
            "app_usage": {
                "installed_apps": ["WhatsApp", "Instagram", "HDFC Bank", "Paytm", "Swiggy"],
                "screen_time_minutes": 360,
                "sessions_count": 18,
                "top_app": "WhatsApp",
                "apps_opened_today": 15
            },
            "network_behavior": {
                "data_usage_mb": 1200,
                "wifi_usage_mb": 900,
                "cellular_usage_mb": 300,
                "wifi_networks": ["Home_WiFi", "Office_WiFi", "Starbucks_WiFi"],
                "data_saver": True
            },
            "location_data": {
                "locations": [
                    {"lat": 12.9716, "lng": 77.5946, "timestamp": "2024-01-15T09:00:00Z"},
                    {"lat": 12.9352, "lng": 77.6245, "timestamp": "2024-01-15T17:30:00Z"}
                ],
                "avg_accuracy": 10.5,
                "places_visited": 4,
                "distance_km": 32.8
            }
        }
        
        # Test device data processing
        result = self.device_collector.process_device_data(device_data)
        
        if result.success:
            print(f"✅ Device data processing successful:")
            print(f"   Records processed: {result.records_collected}")
            print(f"   Collection timestamp: {result.collection_timestamp}")
            print(f"   User ID: {result.metadata.get('user_id')}")
            
            # Show processed data
            if result.data is not None and not result.data.empty:
                print(f"   Processed data shape: {result.data.shape}")
                processed_row = result.data.iloc[0]
                
                print(f"\\n   Sample processed features:")
                for col in ['device_model', 'operating_system', 'installed_apps_count', 
                           'daily_screen_time_minutes', 'daily_data_usage_mb']:
                    if col in processed_row:
                        print(f"     {col}: {processed_row[col]}")
            
            return result
        else:
            print(f"❌ Device data processing failed:")
            print(f"   Error: {result.error_message}")
            return None
    
    def test_collector_status(self):
        """Test collector status."""
        print(f"\\n📊 Testing Collector Status")
        print("-" * 50)
        
        aa_status = self.aa_collector.get_status()
        device_status = self.device_collector.get_status()
        
        print(f"Account Aggregator Collector:")
        print(f"   Name: {aa_status['name']}")
        print(f"   Data source type: {aa_status['data_source_type']}")
        print(f"   Is configured: {aa_status['is_configured']}")
        print(f"   Connection valid: {aa_status['connection_valid']}")
        print(f"   Last collection: {aa_status['last_collection_time']}")
        
        print(f"\\nDevice Data Collector:")
        print(f"   Name: {device_status['name']}")
        print(f"   Data source type: {device_status['data_source_type']}")
        print(f"   Is configured: {device_status['is_configured']}")
        print(f"   Connection valid: {device_status['connection_valid']}")
        print(f"   Last collection: {device_status['last_collection_time']}")
        
        print(f"\\nActive consents: {len(self.aa_collector.active_consents)}")
    
    def run_complete_test(self):
        """Run complete test suite."""
        print("=" * 80)
        print("🏦 ACCOUNT AGGREGATOR COLLECTOR DIRECT TEST")
        print("=" * 80)
        
        user_id = f"test_user_{int(time.time())}"
        
        try:
            # Test 1: Configuration
            if not self.test_aa_collector_configuration():
                print("❌ Configuration test failed")
                return False
            
            # Test 2: Consent creation
            consent = self.test_consent_creation(user_id)
            if not consent or consent.status == ConsentStatus.DENIED:
                print("❌ Consent creation test failed")
                return False
            
            # Test 3: Consent status monitoring
            if not self.test_consent_status_monitoring(consent.consent_handle):
                print("❌ Consent status monitoring test failed")
                return False
            
            # Test 4: FI data request
            session_id = self.test_fi_data_request(consent.consent_handle)
            if not session_id:
                print("❌ FI data request test failed")
                return False
            
            # Test 5: FI data fetch
            if not self.test_fi_data_fetch(session_id):
                print("❌ FI data fetch test failed")
                return False
            
            # Test 6: Device data collection
            if not self.test_device_data_collection(user_id):
                print("❌ Device data collection test failed")
                return False
            
            # Test 7: Collector status
            self.test_collector_status()
            
            print("\\n" + "=" * 80)
            print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
            print("=" * 80)
            print(f"   Test User ID: {user_id}")
            print(f"   Consent Handle: {consent.consent_handle}")
            print(f"   Session ID: {session_id}")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\\n❌ Test suite failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main test function."""
    print("🔧 Direct Account Aggregator Collector Test")
    print("=" * 60)
    
    # Create tester
    tester = AACollectorTester()
    
    # Run complete test
    success = tester.run_complete_test()
    
    if success:
        print("\\n✅ All direct tests passed!")
        return 0
    else:
        print("\\n❌ Some direct tests failed!")
        return 1


if __name__ == "__main__":
    exit(main())
