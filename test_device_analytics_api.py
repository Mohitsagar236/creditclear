"""
Test Device Analytics API Integration

This script tests the device analytics API endpoints to ensure
proper integration between React Native frontend and FastAPI backend.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any
import sys

# API Configuration
API_BASE_URL = "http://localhost:8000"
DEVICE_ANALYTICS_ENDPOINT = f"{API_BASE_URL}/device-analytics"

def create_sample_device_profile() -> Dict[str, Any]:
    """Create a realistic sample device profile for testing"""
    return {
        "profileVersion": "1.0.0",
        "collectedAt": datetime.utcnow().isoformat() + "Z",
        "collectionTimeMs": 1250,
        "device": {
            "deviceId": "test-device-12345",
            "deviceType": "Smartphone",
            "brand": "Samsung",
            "manufacturer": "Samsung",
            "model": "Galaxy S21",
            "deviceName": "Samsung Galaxy S21",
            "systemName": "Android",
            "systemVersion": "13",
            "buildNumber": "123456",
            "appVersion": "1.0.0",
            "buildVersion": "100",
            "bundleId": "com.creditclear.app",
            "isTablet": False,
            "hasNotch": True,
            "hasDynamicIsland": False,
            "isPinOrFingerprintSet": True,
            "supportedAbis": ["arm64-v8a", "armeabi-v7a"],
            "totalMemory": 8589934592,  # 8GB
            "usedMemory": 4294967296,   # 4GB
            "totalDiskCapacity": 128849018880,  # 120GB
            "freeDiskStorage": 85899345920,     # 80GB
            "batteryLevel": 0.85,
            "powerState": {"isCharging": False, "batteryLevel": 0.85},
            "isEmulator": False,
            "platform": "android",
            "platformVersion": "13",
            "screenInfo": {
                "screenWidth": 1080,
                "screenHeight": 2400,
                "windowWidth": 1080,
                "windowHeight": 2400,
                "pixelRatio": 3.0,
                "fontScale": 1.0
            },
            "androidInfo": {
                "androidId": "abc123def456",
                "apiLevel": 33,
                "securityPatch": "2024-01-01",
                "codename": "TIRAMISU",
                "incremental": "123456.789",
                "installerPackageName": "com.android.vending"
            }
        },
        "network": {
            "type": "wifi",
            "isConnected": True,
            "isInternetReachable": True,
            "details": {
                "isConnectionExpensive": False,
                "ssid": "HomeWiFi",
                "bssid": "aa:bb:cc:dd:ee:ff",
                "strength": -45,
                "ipAddress": "192.168.1.100",
                "subnet": "255.255.255.0"
            }
        },
        "apps": {
            "banking": [],
            "investment": [],
            "lending": [],
            "totalCount": 0,
            "note": "App scanning disabled for Google Play compliance"
        },
        "permissions": {
            "location": "granted",
            "camera": "granted",
            "microphone": "denied",
            "storage": "granted",
            "contacts": "not_determined",
            "notifications": "granted",
            "biometric": "granted",
            "phone": "granted",
            "sms": "denied"
        },
        "riskFlags": {
            "isEmulator": False,
            "isRooted": False,
            "isJailbroken": False,
            "hasSecurityFeatures": True,
            "isDebuggingEnabled": False
        },
        "dataUsage": {
            "purpose": "Credit risk assessment and fraud prevention",
            "retention": "90 days",
            "sharing": "Not shared with third parties",
            "userConsent": "Required before collection"
        }
    }

def create_high_risk_device_profile() -> Dict[str, Any]:
    """Create a high-risk device profile for testing"""
    profile = create_sample_device_profile()
    
    # Modify to create high-risk flags
    profile["device"]["isEmulator"] = True
    profile["riskFlags"]["isEmulator"] = True
    profile["riskFlags"]["isRooted"] = True
    profile["riskFlags"]["hasSecurityFeatures"] = False
    profile["riskFlags"]["isDebuggingEnabled"] = True
    profile["device"]["isPinOrFingerprintSet"] = False
    profile["device"]["systemVersion"] = "8"  # Old Android version
    
    return profile

def test_submit_device_analytics():
    """Test submitting device analytics to the API"""
    print("🧪 Testing device analytics submission...")
    
    # Test data
    request_data = {
        "user_id": "test_user_123",
        "device_profile": create_sample_device_profile(),
        "collection_timestamp": datetime.utcnow().isoformat() + "Z",
        "app_version": "1.0.0",
        "consent_given": True,
        "collection_purpose": "credit_risk_assessment"
    }
    
    try:
        response = requests.post(
            f"{DEVICE_ANALYTICS_ENDPOINT}/submit",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Device analytics submission successful!")
            print(f"   Analytics ID: {result.get('analytics_id')}")
            print(f"   Risk Score: {result.get('risk_score')}")
            print(f"   Risk Level: {result.get('risk_level')}")
            print(f"   Recommendations: {len(result.get('recommendations', []))}")
            
            return result
        else:
            print(f"❌ Device analytics submission failed!")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_high_risk_device():
    """Test submitting high-risk device analytics"""
    print("\n🚨 Testing high-risk device analytics...")
    
    request_data = {
        "user_id": "high_risk_user_456",
        "device_profile": create_high_risk_device_profile(),
        "collection_timestamp": datetime.utcnow().isoformat() + "Z",
        "app_version": "1.0.0",
        "consent_given": True,
        "collection_purpose": "credit_risk_assessment"
    }
    
    try:
        response = requests.post(
            f"{DEVICE_ANALYTICS_ENDPOINT}/submit",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ High-risk device analytics processed!")
            print(f"   Risk Score: {result.get('risk_score')}")
            print(f"   Risk Level: {result.get('risk_level')}")
            print(f"   Risk Factors: {len(result.get('recommendations', []))}")
            
            # Verify high risk was detected
            if result.get('risk_level') in ['medium', 'high']:
                print("✅ High risk properly detected!")
            else:
                print("⚠️  Expected higher risk level")
                
            return result
        else:
            print(f"❌ High-risk device test failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_get_risk_profile():
    """Test retrieving user risk profile"""
    print("\n📊 Testing risk profile retrieval...")
    
    user_id = "test_user_123"
    
    try:
        response = requests.get(
            f"{DEVICE_ANALYTICS_ENDPOINT}/risk-profile/{user_id}",
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Risk profile retrieved successfully!")
            print(f"   User ID: {result.get('user_id')}")
            print(f"   Risk Score: {result.get('risk_score')}")
            print(f"   Risk Level: {result.get('risk_level')}")
            print(f"   Device Count: {result.get('device_count')}")
            
            return result
        else:
            print(f"❌ Risk profile retrieval failed: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None

def test_invalid_requests():
    """Test API validation with invalid requests"""
    print("\n🛡️  Testing API validation...")
    
    # Test missing user consent
    invalid_request = {
        "user_id": "test_user",
        "device_profile": create_sample_device_profile(),
        "collection_timestamp": datetime.utcnow().isoformat() + "Z",
        "app_version": "1.0.0",
        "consent_given": False,  # Invalid - no consent
        "collection_purpose": "credit_risk_assessment"
    }
    
    try:
        response = requests.post(
            f"{DEVICE_ANALYTICS_ENDPOINT}/submit",
            json=invalid_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 422:  # Validation error expected
            print("✅ Consent validation working correctly")
        else:
            print(f"⚠️  Unexpected response for no consent: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
    
    # Test empty user ID
    invalid_request["consent_given"] = True
    invalid_request["user_id"] = ""
    
    try:
        response = requests.post(
            f"{DEVICE_ANALYTICS_ENDPOINT}/submit",
            json=invalid_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 422:  # Validation error expected
            print("✅ User ID validation working correctly")
        else:
            print(f"⚠️  Unexpected response for empty user ID: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")

def test_health_check():
    """Test health check endpoint"""
    print("\n🏥 Testing health check...")
    
    try:
        response = requests.get(
            f"{DEVICE_ANALYTICS_ENDPOINT}/health",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {result.get('status')}")
            print(f"   Service: {result.get('service')}")
            print(f"   Version: {result.get('version')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check request failed: {str(e)}")

def main():
    """Run all device analytics tests"""
    print("🚀 Starting Device Analytics API Tests")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not running. Please start the server with:")
            print("   python -m uvicorn src.api.main:app --reload")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API. Please ensure the server is running:")
        print("   python -m uvicorn src.api.main:app --reload")
        sys.exit(1)
    
    print("✅ API is running, proceeding with tests...\n")
    
    # Run tests
    test_health_check()
    test_submit_device_analytics()
    test_high_risk_device()
    test_get_risk_profile()
    test_invalid_requests()
    
    print("\n" + "=" * 50)
    print("🎉 Device Analytics API Tests Complete!")
    print("\n📱 Next Steps:")
    print("1. Integrate DeviceAnalytics.js in your React Native app")
    print("2. Test data collection on real devices")
    print("3. Configure production database storage")
    print("4. Set up monitoring and alerts")
    print("5. Review and update privacy policies")

if __name__ == "__main__":
    main()
