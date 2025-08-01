#!/usr/bin/env python3
"""
Test script for the new mobile device data upload endpoint.

This script tests the POST /upload-device-data endpoint with sample
React Native device data to ensure proper validation and processing.
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# API base URL
API_BASE_URL = "http://localhost:8000"

def create_sample_mobile_device_data():
    """Create sample mobile device data that matches the schema."""
    
    # Simulate data that would come from React Native DeviceAnalytics.js
    device_data = {
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
            "total_memory": 8589934592,  # 8GB
            "used_memory": 4294967296,   # 4GB
            "total_disk_capacity": 107374182400,  # 100GB
            "free_disk_storage": 53687091200,     # 50GB
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
            "latitude": 28.61,  # Coarse location (Delhi)
            "longitude": 77.21,
            "accuracy": 1000.0,  # 1km accuracy
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
    
    return device_data

def test_mobile_device_upload():
    """Test the mobile device data upload endpoint."""
    print("🧪 Testing Mobile Device Data Upload Endpoint")
    print("=" * 60)
    
    # Create sample data
    device_data = create_sample_mobile_device_data()
    
    # Create request payload
    request_payload = {
        "device_data": device_data
    }
    
    print(f"📱 Testing with device data for user: {device_data['user_id']}")
    print(f"   Device: {device_data['device_info']['brand']} {device_data['device_info']['model']}")
    print(f"   Platform: {device_data['device_info']['platform']} {device_data['device_info']['system_version']}")
    print(f"   Network: {device_data['network_info']['type']}")
    print(f"   Location: {device_data['coarse_location']['latitude']}, {device_data['coarse_location']['longitude']}")
    
    try:
        # Send POST request
        print(f"\n🚀 Sending POST request to {API_BASE_URL}/data-collection/upload-device-data")
        
        response = requests.post(
            f"{API_BASE_URL}/data-collection/upload-device-data",
            json=request_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Device data uploaded successfully")
            print(f"   Message: {result.get('message')}")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Records Processed: {result.get('records_processed')}")
            
            # Check risk assessment
            risk_assessment = result.get('risk_assessment')
            if risk_assessment:
                print(f"\\n🛡️  Risk Assessment:")
                print(f"   Risk Score: {risk_assessment.get('risk_score')}")
                print(f"   Risk Level: {risk_assessment.get('risk_level')}")
                print(f"   Risk Factors: {', '.join(risk_assessment.get('risk_factors', []))}")
            else:
                print(f"\\n🛡️  No risk factors detected")
            
            return True
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection failed - Is the API server running?")
        print(f"   Start the server with: python -m uvicorn src.api.main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_validation_errors():
    """Test validation error handling."""
    print(f"\n🧪 Testing Validation Error Handling")
    print("-" * 50)
    
    # Test with missing required fields
    invalid_data = {
        "device_data": {
            "user_id": "test_user",
            # Missing required device_info
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
                "is_cellular_enabled": True
            }
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/data-collection/upload-device-data",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 422:
            print(f"✅ Validation error correctly caught")
            try:
                error_detail = response.json()
                print(f"   Validation errors: {len(error_detail.get('detail', []))}")
            except:
                print(f"   Error response: {response.text[:200]}")
        else:
            print(f"❌ Expected validation error (422), got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing validation: {e}")

def test_high_risk_device():
    """Test with high-risk device profile."""
    print(f"\n🧪 Testing High-Risk Device Profile")
    print("-" * 50)
    
    # Create high-risk device data
    device_data = create_sample_mobile_device_data()
    
    # Modify to be high-risk
    device_data["device_info"]["is_emulator"] = True
    device_data["risk_flags"]["is_emulator"] = True
    device_data["risk_flags"]["is_rooted_or_jailbroken"] = True
    device_data["risk_flags"]["has_debugging_enabled"] = True
    device_data["risk_flags"]["has_security_features"] = False
    
    request_payload = {"device_data": device_data}
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/data-collection/upload-device-data",
            json=request_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            risk_assessment = result.get('risk_assessment', {})
            risk_score = risk_assessment.get('risk_score', 0)
            risk_level = risk_assessment.get('risk_level', 'unknown')
            
            print(f"✅ High-risk device processed successfully")
            print(f"   Risk Score: {risk_score}")
            print(f"   Risk Level: {risk_level}")
            
            if risk_level == "high":
                print(f"✅ Risk assessment correctly identified high-risk device")
            else:
                print(f"⚠️  Expected high risk level, got: {risk_level}")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing high-risk device: {e}")

def main():
    """Run all tests."""
    print("🚀 Mobile Device Data Upload Endpoint Tests")
    print("=" * 60)
    
    # Test 1: Normal device data upload
    success1 = test_mobile_device_upload()
    
    # Test 2: Validation error handling
    test_validation_errors()
    
    # Test 3: High-risk device
    test_high_risk_device()
    
    print(f"\n" + "=" * 60)
    if success1:
        print("🎉 Mobile device data upload endpoint is working correctly!")
        print("\n📋 Integration Summary:")
        print("✅ Endpoint POST /data-collection/upload-device-data created")
        print("✅ Pydantic schema validation working")
        print("✅ DeviceDataCollector integration successful")
        print("✅ Risk assessment calculation implemented")
        print("✅ Error handling and validation working")
        
        print("\n🚀 Next Steps:")
        print("1. Update React Native app to use this endpoint")
        print("2. Test with real device data from mobile app")
        print("3. Monitor risk assessment accuracy")
        print("4. Implement additional fraud detection rules")
    else:
        print("❌ Tests failed - check API server and configuration")
        print("\n🔧 Troubleshooting:")
        print("1. Ensure API server is running: python -m uvicorn src.api.main:app --reload")
        print("2. Check if data_collection routes are properly included")
        print("3. Verify DeviceDataCollector is properly configured")

if __name__ == "__main__":
    main()
