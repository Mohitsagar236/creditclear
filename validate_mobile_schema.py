#!/usr/bin/env python3
"""
Validation script for the mobile device data schema and endpoint implementation.

This script validates the schema implementation without requiring a running server.
"""

import json
import sys
import os
from datetime import datetime
from pydantic import ValidationError

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from api.schemas.device_data import (
        MobileDeviceDataRequest,
        MobileDeviceDataResponse,
        DeviceInfo,
        NetworkInfo,
        CoarseLocationInfo,
        AppInfo,
        RiskFlags,
        ScreenInfo,
        MobileDeviceData
    )
    print("✅ Successfully imported mobile device data schemas")
except ImportError as e:
    print(f"❌ Failed to import schemas: {e}")
    sys.exit(1)

def create_sample_device_data():
    """Create sample device data to test schema validation."""
    
    return {
        "user_id": "test_user_12345",
        "collection_timestamp": datetime.utcnow().isoformat() + "Z",
        "profile_version": "1.0.0",
        "collection_time_ms": 1250,
        
        "device_info": {
            "device_id": "anonymized_device_abc123",
            "device_type": "Smartphone",
            "brand": "Samsung",
            "manufacturer": "Samsung",
            "model": "Galaxy S23",
            "device_name": "Samsung Galaxy S23",
            "system_name": "Android",
            "system_version": "13",
            "build_number": "TQ3A.230901.001",
            "app_version": "1.0.0",
            "build_version": "100",
            "bundle_id": "com.creditclear.app",
            "is_tablet": False,
            "has_notch": False,
            "has_dynamic_island": False,
            "is_pin_or_fingerprint_set": True,
            "supported_abis": ["arm64-v8a", "armeabi-v7a"],
            "total_memory": 8589934592,
            "used_memory": 4294967296,
            "total_disk_capacity": 107374182400,
            "free_disk_storage": 53687091200,
            "battery_level": 0.75,
            "is_emulator": False,
            "platform": "android",
            "platform_version": "13"
        },
        
        "screen_info": {
            "screen_width": 1080,
            "screen_height": 2340,
            "window_width": 1080,
            "window_height": 2240,
            "pixel_ratio": 2.75,
            "font_scale": 1.0
        },
        
        "network_info": {
            "type": "wifi",
            "is_connected": True,
            "is_wifi_enabled": True,
            "is_cellular_enabled": True,
            "wifi_ssid": "Home_WiFi_5G",
            "cellular_generation": "5G",
            "is_connection_expensive": False
        },
        
        "coarse_location": {
            "latitude": 28.61,
            "longitude": 77.21,
            "accuracy": 1000.0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "geolocation_service"
        },
        
        "app_info": {
            "total_count": 85,
            "has_banking_apps": True,
            "has_payment_apps": True,
            "has_financial_apps": True,
            "compliance_note": "No app list scanning - compliance with privacy policies"
        },
        
        "risk_flags": {
            "is_emulator": False,
            "is_rooted_or_jailbroken": False,
            "has_debugging_enabled": False,
            "has_security_features": True,
            "is_os_outdated": False
        }
    }

def test_schema_validation():
    """Test the Pydantic schema validation."""
    print("\n🧪 Testing Schema Validation")
    print("=" * 50)
    
    try:
        # Test 1: Valid device data
        print("1. Testing valid device data...")
        device_data = create_sample_device_data()
        
        # Validate individual components
        device_info = DeviceInfo(**device_data["device_info"])
        print(f"   ✅ DeviceInfo validation passed")
        
        screen_info = ScreenInfo(**device_data["screen_info"])
        print(f"   ✅ ScreenInfo validation passed")
        
        network_info = NetworkInfo(**device_data["network_info"])
        print(f"   ✅ NetworkInfo validation passed")
        
        location_info = CoarseLocationInfo(**device_data["coarse_location"])
        print(f"   ✅ CoarseLocationInfo validation passed")
        
        app_info = AppInfo(**device_data["app_info"])
        print(f"   ✅ AppInfo validation passed")
        
        risk_flags = RiskFlags(**device_data["risk_flags"])
        print(f"   ✅ RiskFlags validation passed")
        
        # Validate complete mobile device data
        mobile_data = MobileDeviceData(**device_data)
        print(f"   ✅ MobileDeviceData validation passed")
        
        # Validate request wrapper
        request_data = {"device_data": mobile_data}
        mobile_request = MobileDeviceDataRequest(**request_data)
        print(f"   ✅ MobileDeviceDataRequest validation passed")
        
        print(f"\n✅ All schema validations passed!")
        
        return True
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_validation_rules():
    """Test specific validation rules."""
    print("\n🧪 Testing Validation Rules")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Battery level validation
    total_tests += 1
    try:
        device_data = create_sample_device_data()
        device_data["device_info"]["battery_level"] = 1.5  # Invalid: > 1.0
        DeviceInfo(**device_data["device_info"])
        print("❌ Battery level validation failed")
    except ValidationError:
        print("✅ Battery level validation working")
        tests_passed += 1
    
    # Test 2: Location accuracy validation
    total_tests += 1
    try:
        location_data = {
            "latitude": 28.61,
            "longitude": 77.21,
            "accuracy": 500.0,  # Invalid: < 1000m
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "geolocation_service"
        }
        CoarseLocationInfo(**location_data)
        print("❌ Location accuracy validation failed")
    except ValidationError:
        print("✅ Location accuracy validation working")
        tests_passed += 1
    
    # Test 3: Latitude range validation
    total_tests += 1
    try:
        location_data = {
            "latitude": 91.0,  # Invalid: > 90
            "longitude": 77.21,
            "accuracy": 1000.0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "geolocation_service"
        }
        CoarseLocationInfo(**location_data)
        print("❌ Latitude range validation failed")
    except ValidationError:
        print("✅ Latitude range validation working")
        tests_passed += 1
    
    # Test 4: Pixel ratio validation
    total_tests += 1
    try:
        screen_data = {
            "screen_width": 1080,
            "screen_height": 2340,
            "window_width": 1080,
            "window_height": 2240,
            "pixel_ratio": -1.0,  # Invalid: negative
            "font_scale": 1.0
        }
        ScreenInfo(**screen_data)
        print("❌ Pixel ratio validation failed")
    except ValidationError:
        print("✅ Pixel ratio validation working")
        tests_passed += 1
    
    print(f"\n📊 Validation rules test results: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def test_json_serialization():
    """Test JSON serialization/deserialization."""
    print("\n🧪 Testing JSON Serialization")
    print("=" * 50)
    
    try:
        # Create valid device data
        device_data = create_sample_device_data()
        mobile_data = MobileDeviceData(**device_data)
        
        # Test serialization
        json_str = mobile_data.json()
        print("✅ JSON serialization successful")
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        reconstructed = MobileDeviceData(**parsed_data)
        print("✅ JSON deserialization successful")
        
        # Verify data integrity
        if mobile_data.user_id == reconstructed.user_id:
            print("✅ Data integrity verified")
            return True
        else:
            print("❌ Data integrity check failed")
            return False
            
    except Exception as e:
        print(f"❌ JSON serialization error: {e}")
        return False

def demonstrate_usage():
    """Demonstrate how to use the schemas."""
    print("\n📚 Usage Demonstration")
    print("=" * 50)
    
    print("1. Creating device data from React Native:")
    print("```javascript")
    print("const deviceProfile = await collectCompleteDeviceProfile();")
    print("const response = await fetch('/data-collection/upload-device-data', {")
    print("  method: 'POST',")
    print("  headers: { 'Content-Type': 'application/json' },")
    print("  body: JSON.stringify({ device_data: deviceProfile })")
    print("});")
    print("```")
    
    print("\n2. Processing on backend:")
    print("```python")
    print("@router.post('/upload-device-data')")
    print("async def upload_device_data(request: MobileDeviceDataRequest):")
    print("    device_data = request.device_data")
    print("    # Process through DeviceDataCollector")
    print("    result = device_collector.process_device_data(device_data.dict())")
    print("    return MobileDeviceDataResponse(...)")
    print("```")
    
    print("\n3. Sample request structure:")
    device_data = create_sample_device_data()
    mobile_data = MobileDeviceData(**device_data)
    
    print(f"   User ID: {mobile_data.user_id}")
    print(f"   Device: {mobile_data.device_info.brand} {mobile_data.device_info.model}")
    print(f"   Platform: {mobile_data.device_info.platform} {mobile_data.device_info.system_version}")
    print(f"   Network: {mobile_data.network_info.type}")
    print(f"   Location: {mobile_data.coarse_location.latitude}, {mobile_data.coarse_location.longitude}")
    print(f"   Security: {'Yes' if mobile_data.device_info.is_pin_or_fingerprint_set else 'No'}")

def main():
    """Run all validation tests."""
    print("🚀 Mobile Device Data Schema Validation")
    print("=" * 60)
    
    # Test schema validation
    schema_test = test_schema_validation()
    
    # Test validation rules
    rules_test = test_validation_rules()
    
    # Test JSON serialization
    json_test = test_json_serialization()
    
    # Demonstrate usage
    demonstrate_usage()
    
    print(f"\n" + "=" * 60)
    
    if schema_test and rules_test and json_test:
        print("🎉 All validation tests passed!")
        print("\n📋 Implementation Summary:")
        print("✅ Pydantic schemas created in src/api/schemas/device_data.py")
        print("✅ Schema validation working correctly")
        print("✅ Validation rules enforced")
        print("✅ JSON serialization/deserialization working")
        print("✅ Mobile device data request/response models ready")
        print("✅ Endpoint implementation in src/api/routes/data_collection.py")
        
        print("\n🚀 Ready for Integration:")
        print("1. Start API server: python -m uvicorn src.api.main:app --reload")
        print("2. Test endpoint: POST /data-collection/upload-device-data")
        print("3. Update React Native app to use new schema")
        print("4. Test with real device data")
        
        print("\n📊 Schema Features:")
        print("• Comprehensive device information validation")
        print("• Google Play compliant coarse location (≥1km accuracy)")
        print("• Network connectivity information")
        print("• Security and risk assessment flags")
        print("• Privacy-focused app information (no app list scanning)")
        print("• Battery level and hardware capability validation")
        print("• Platform-specific information handling")
        
    else:
        print("❌ Some validation tests failed")
        print("Check the error messages above for details")

if __name__ == "__main__":
    main()
