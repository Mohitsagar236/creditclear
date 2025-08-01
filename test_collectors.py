#!/usr/bin/env python3
"""
Test script for the data collectors module.

This script demonstrates how to use the BaseCollector abstract class
and its concrete implementations: AccountAggregatorCollector and DeviceDataCollector.
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_processing.collectors import (
        BaseCollector, AccountAggregatorCollector, DeviceDataCollector,
        DataSourceType, ConsentStatus, ConsentRequest, CollectionResult
    )
    print("✅ Successfully imported data collectors")
except ImportError as e:
    print(f"❌ Failed to import collectors: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)

def test_account_aggregator_collector():
    """Test the Account Aggregator collector functionality."""
    print("\n🏦 Testing Account Aggregator Collector")
    print("=" * 60)
    
    # Initialize collector
    aa_collector = AccountAggregatorCollector()
    
    # Test configuration
    config = {
        "api_base_url": "https://api.accountaggregator.example.com",
        "client_id": "test_client_123",
        "client_secret": "test_secret_456",
        "consent_timeout": 300
    }
    
    print("📋 Configuring Account Aggregator collector...")
    success = aa_collector.configure(config)
    print(f"   Configuration: {'✅ Success' if success else '❌ Failed'}")
    
    # Test connection validation
    print("🔍 Validating connection...")
    connection_valid = aa_collector.validate_connection()
    print(f"   Connection: {'✅ Valid' if connection_valid else '❌ Invalid'}")
    
    # Test status
    status = aa_collector.get_status()
    print(f"📊 Collector Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Test consent initiation
    print(f"\n🤝 Testing consent flow...")
    user_id = "user_12345"
    consent = aa_collector.initiate_consent(
        user_id=user_id,
        data_types=["bank_account", "credit_card"],
        purpose="Credit Risk Assessment",
        duration_days=30
    )
    
    print(f"   Consent Handle: {consent.consent_handle}")
    print(f"   Consent Status: {consent.status.value}")
    print(f"   Expires At: {consent.expires_at}")
    
    # Test consent status check
    print(f"\n🔄 Checking consent status...")
    initial_status = aa_collector.check_consent_status(consent.consent_handle)
    print(f"   Initial Status: {initial_status.value}")
    
    # Simulate waiting for consent approval
    print(f"   ⏳ Simulating consent approval process...")
    import time
    time.sleep(2)  # Wait 2 seconds
    
    updated_status = aa_collector.check_consent_status(consent.consent_handle)
    print(f"   Updated Status: {updated_status.value}")
    
    # Test data collection with consent
    print(f"\n📊 Testing data collection...")
    if updated_status == ConsentStatus.GRANTED:
        result = aa_collector.fetch_data(consent.consent_handle)
        print(f"   Collection Success: {result.success}")
        print(f"   Records Collected: {result.records_collected}")
        
        if result.data is not None:
            print(f"   Data Sample:")
            print(result.data.head(3).to_string(index=False))
            print(f"   Data Shape: {result.data.shape}")
    else:
        print(f"   ⏳ Consent not yet granted, testing with collect_data method...")
        
        # Test the main collect_data method
        result = aa_collector.collect_data(
            user_id=user_id,
            data_types=["bank_account"],
            purpose="Credit Assessment"
        )
        print(f"   Collection Success: {result.success}")
        print(f"   Metadata: {result.metadata}")

def test_device_data_collector():
    """Test the Device Data collector functionality."""
    print("\n📱 Testing Device Data Collector")
    print("=" * 60)
    
    # Initialize collector
    device_collector = DeviceDataCollector()
    
    # Test configuration
    config = {
        "validation_rules": {
            "min_data_points": 5,
            "required_fields": ["user_id", "device_info"]
        },
        "supported_data_types": [
            "device_info", "app_usage", "network_behavior", "location_data"
        ],
        "privacy_settings": {
            "anonymize_location": True,
            "data_retention_days": 90
        }
    }
    
    print("📋 Configuring Device Data collector...")
    success = device_collector.configure(config)
    print(f"   Configuration: {'✅ Success' if success else '❌ Failed'}")
    
    # Test connection validation
    print("🔍 Validating connection...")
    connection_valid = device_collector.validate_connection()
    print(f"   Connection: {'✅ Valid' if connection_valid else '❌ Invalid'}")
    
    # Test status
    status = device_collector.get_status()
    print(f"📊 Collector Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Create sample device data
    sample_device_data = {
        "user_id": "user_12345",
        "timestamp": datetime.now().isoformat(),
        "device_info": {
            "model": "iPhone 14 Pro",
            "os": "iOS",
            "os_version": "16.5.1",
            "screen_resolution": "1179x2556",
            "storage_gb": 256,
            "ram_gb": 6
        },
        "app_usage": {
            "installed_apps": [
                "Chase Mobile", "PayPal", "Venmo", "Netflix", "Instagram",
                "WhatsApp", "Uber", "Spotify", "Gmail", "Chrome"
            ],
            "screen_time_minutes": 420,
            "sessions_count": 35,
            "top_app": "Instagram",
            "apps_opened_today": 8
        },
        "network_behavior": {
            "data_usage_mb": 1250,
            "wifi_usage_mb": 950,
            "cellular_usage_mb": 300,
            "wifi_networks": ["Home_WiFi", "Office_WiFi", "Starbucks_WiFi"],
            "data_saver": False
        },
        "location_data": {
            "locations": [
                {"lat": 40.7128, "lon": -74.0060, "timestamp": "2024-01-15T09:00:00"},
                {"lat": 40.7589, "lon": -73.9851, "timestamp": "2024-01-15T12:30:00"},
                {"lat": 40.7128, "lon": -74.0060, "timestamp": "2024-01-15T18:00:00"}
            ],
            "avg_accuracy": 10.5,
            "places_visited": 3,
            "distance_km": 12.5
        }
    }
    
    print(f"\n📊 Testing device data processing...")
    print(f"   Processing data for user: {sample_device_data['user_id']}")
    
    # Test processing device data
    result = device_collector.process_device_data(sample_device_data)
    print(f"   Processing Success: {result.success}")
    print(f"   Records Processed: {result.records_collected}")
    
    if result.data is not None:
        print(f"   Processed Data:")
        for col in result.data.columns:
            if col not in ['user_id', 'collection_timestamp']:
                value = result.data.iloc[0][col]
                print(f"     {col}: {value}")
    
    # Test with JSON string input
    print(f"\n🔄 Testing with JSON string input...")
    json_data = json.dumps(sample_device_data)
    json_result = device_collector.process_device_data(json_data)
    print(f"   JSON Processing Success: {json_result.success}")
    
    # Test the main collect_data method
    print(f"\n📱 Testing collect_data method...")
    collect_result = device_collector.collect_data(
        user_id="user_12345",
        device_data=sample_device_data
    )
    print(f"   Collection Success: {collect_result.success}")
    print(f"   Metadata: {collect_result.metadata}")
    
    # Test error handling
    print(f"\n❌ Testing error handling...")
    invalid_data = {"invalid": "data"}
    error_result = device_collector.process_device_data(invalid_data)
    print(f"   Error Handling Success: {not error_result.success}")
    print(f"   Error Message: {error_result.error_message}")

def test_data_source_types():
    """Test data source type enumeration."""
    print("\n📋 Testing Data Source Types")
    print("=" * 60)
    
    print("Available data source types:")
    for source_type in DataSourceType:
        print(f"   - {source_type.name}: {source_type.value}")
    
    print(f"\nConsent status options:")
    for status in ConsentStatus:
        print(f"   - {status.name}: {status.value}")

def main():
    """Main function to run all tests."""
    print("🧪 Data Collectors Test Suite")
    print("=" * 70)
    
    # Test data source types
    test_data_source_types()
    
    # Test Account Aggregator collector
    test_account_aggregator_collector()
    
    # Test Device Data collector
    test_device_data_collector()
    
    print(f"\n" + "=" * 70)
    print("✅ All tests completed!")
    
    print(f"\n💡 Integration Notes:")
    print(f"   - Account Aggregator requires actual API credentials for production use")
    print(f"   - Device Data collector can handle real-time mobile app data")
    print(f"   - Both collectors follow the same BaseCollector interface")
    print(f"   - Additional collectors can be easily added using the same pattern")
    print(f"   - Consent management ensures compliance with data privacy regulations")
    print(f"   - All data collection is logged for audit and monitoring purposes")

if __name__ == "__main__":
    main()
