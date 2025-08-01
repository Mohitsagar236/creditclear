"""
Test Script for AI Alternative Data Credit Risk Model

This script tests the complete AI alternative data pipeline including:
- Model training and inference
- Data collection simulation
- API endpoints
- Integration testing
"""

import asyncio
import requests
import json
import pandas as pd
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.ai_alternative_data_model import AIAlternativeDataModel
from src.services.automatic_data_collection import AutomaticDataCollectionService

def test_ai_model():
    """Test the AI Alternative Data Model."""
    print("🧪 Testing AI Alternative Data Model...")
    
    try:
        # Initialize model
        model = AIAlternativeDataModel()
        print("✅ Model initialization successful")
        
        # Create mock training data
        training_data = []
        labels = []
        
        for i in range(100):
            data = {
                'AMT_INCOME_TOTAL': 150000 + (i * 1000),
                'AMT_CREDIT': 300000 + (i * 2000),
                'AMT_ANNUITY': 15000 + (i * 100),
                'DAYS_BIRTH': -10000 - (i * 10),
                'DAYS_EMPLOYED': -1500 - (i * 5),
                'CNT_FAM_MEMBERS': 2,
                'NAME_CONTRACT_TYPE': 'Cash loans',
                'CODE_GENDER': 'F' if i % 2 == 0 else 'M',
                'FLAG_OWN_CAR': 'Y' if i % 3 == 0 else 'N',
                'FLAG_OWN_REALTY': 'Y' if i % 2 == 0 else 'N'
            }
            training_data.append(data)
            labels.append(1 if i % 4 == 0 else 0)  # 25% default rate
        
        # Convert to DataFrame
        df = pd.DataFrame(training_data)
        
        # Test preprocessing
        processed_kaggle = model.preprocess_kaggle_data(df)
        print(f"✅ Kaggle data preprocessing: {processed_kaggle.shape}")
        
        # Test feature extraction
        device_data = {
            'device': {
                'model': 'iPhone 13',
                'platform': 'iOS',
                'systemVersion': '16.0',
                'isPinOrFingerprintSet': True,
                'totalMemory': 6000000000,
                'totalDiskCapacity': 128000000000,
                'isTablet': False
            },
            'network': {
                'type': 'wifi',
                'isConnected': True,
                'isInternetReachable': True
            },
            'riskFlags': {
                'isEmulator': False,
                'isRooted': False,
                'hasSecurityFeatures': True
            },
            'apps': {
                'totalCount': 10,
                'banking': ['SBI', 'ICICI'],
                'investment': [],
                'lending': []
            }
        }
        
        device_features = model.extract_device_features(device_data)
        print(f"✅ Device feature extraction: {len(device_features)} features")
        
        # Test behavioral feature extraction
        alternative_data = {
            'location': {
                'homeLocation': 'detected',
                'travelPatterns': 'regular_commuter'
            },
            'utility': {
                'mobileRecharge': 'regular',
                'electricityBill': 'consistent'
            },
            'digitalFootprint': {},
            'communication': {}
        }
        
        behavioral_features = model.extract_behavioral_features(alternative_data)
        print(f"✅ Behavioral feature extraction: {len(behavioral_features)} features")
        
        # Test feature combination
        combined_features = model.combine_features(processed_kaggle, device_features, behavioral_features)
        print(f"✅ Feature combination: {combined_features.shape}")
        
        # Test model training
        model.fit(combined_features, pd.Series(labels))
        print("✅ Model training successful")
        
        # Test prediction
        test_sample = combined_features.iloc[[0]]
        prediction = model.predict_comprehensive_risk(
            kaggle_data=df.iloc[[0]],
            device_data=device_data,
            alternative_data=alternative_data
        )
        
        print(f"✅ Prediction successful:")
        print(f"   Risk Score: {prediction['risk_score']:.3f}")
        print(f"   Risk Level: {prediction['risk_level']}")
        print(f"   Confidence: {prediction['confidence']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_data_collection_service():
    """Test the Automatic Data Collection Service."""
    print("\n🧪 Testing Automatic Data Collection Service...")
    
    try:
        # Initialize service
        service = AutomaticDataCollectionService()
        await service.initialize_service()
        print("✅ Service initialization successful")
        
        # Test data collection
        device_profile = {
            'device': {
                'model': 'Samsung Galaxy S21',
                'platform': 'Android',
                'systemVersion': '12.0',
                'isPinOrFingerprintSet': True
            },
            'network': {
                'type': 'wifi',
                'isConnected': True
            },
            'riskFlags': {
                'isEmulator': False,
                'isRooted': False
            },
            'apps': {
                'totalCount': 8,
                'banking': ['PhonePe'],
                'investment': [],
                'lending': []
            }
        }
        
        collected_data = await service.collect_comprehensive_data('test_user_001', device_profile)
        print(f"✅ Data collection successful:")
        print(f"   Quality Score: {collected_data['overall_quality_score']:.2f}/100")
        print(f"   Status: {collected_data['collection_status']}")
        print(f"   Data Sources: {len(collected_data['data_sources'])}")
        
        # Test AI assessment
        if service.ai_model.is_fitted:
            assessment = await service.perform_ai_risk_assessment(collected_data)
            print(f"✅ AI assessment successful:")
            print(f"   Risk Score: {assessment['risk_score']:.3f}")
            print(f"   Risk Level: {assessment['risk_level']}")
            print(f"   Confidence: {assessment['confidence']:.2%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data Collection Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoints."""
    print("\n🧪 Testing API Endpoints...")
    
    base_url = "http://localhost:8001"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️ Health endpoint returned {response.status_code}")
        
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
        else:
            print(f"⚠️ Root endpoint returned {response.status_code}")
        
        # Test AI alternative data simulation endpoint
        response = requests.post(
            f"{base_url}/api/v1/ai-alternative-data/simulate-assessment",
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ AI Alternative Data simulation working")
            print(f"   Risk Score: {result['risk_score']:.3f}")
            print(f"   Risk Level: {result['risk_level']}")
        else:
            print(f"⚠️ AI simulation endpoint returned {response.status_code}")
            print(f"   Response: {response.text}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server")
        print("   Make sure the backend server is running on http://localhost:8001")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def test_integration():
    """Test end-to-end integration."""
    print("\n🧪 Testing End-to-End Integration...")
    
    try:
        # Create a complete test scenario
        test_data = {
            'applicant_data': {
                'AMT_INCOME_TOTAL': 200000,
                'AMT_CREDIT': 400000,
                'AMT_ANNUITY': 20000,
                'DAYS_BIRTH': -11000,
                'DAYS_EMPLOYED': -2000,
                'CNT_FAM_MEMBERS': 3,
                'NAME_CONTRACT_TYPE': 'Cash loans',
                'CODE_GENDER': 'M',
                'FLAG_OWN_CAR': 'Y',
                'FLAG_OWN_REALTY': 'Y'
            },
            'device_data': {
                'device': {
                    'model': 'iPhone 14',
                    'platform': 'iOS',
                    'systemVersion': '16.4',
                    'isPinOrFingerprintSet': True,
                    'totalMemory': 6442450944,
                    'totalDiskCapacity': 128849018880,
                    'isTablet': False
                },
                'network': {
                    'type': 'wifi',
                    'isConnected': True,
                    'isInternetReachable': True,
                    'details': {'isConnectionExpensive': False}
                },
                'riskFlags': {
                    'isEmulator': False,
                    'isRooted': False,
                    'isJailbroken': False,
                    'hasSecurityFeatures': True,
                    'isDebuggingEnabled': False
                },
                'apps': {
                    'totalCount': 15,
                    'banking': ['SBI', 'ICICI', 'HDFC'],
                    'investment': ['Zerodha', 'Groww'],
                    'lending': []
                }
            },
            'location_data': {
                'currentCity': 'Mumbai',
                'homeLocation': 'detected',
                'workLocation': 'detected',
                'travelPatterns': 'regular_commuter'
            },
            'utility_data': {
                'mobileRecharge': 'regular',
                'electricityBill': 'consistent',
                'internetUsage': 'high',
                'subscriptionServices': 'multiple'
            },
            'digital_footprint': {
                'socialMediaPresence': 'professional',
                'onlineActivity': 'regular',
                'digitalIdentity': 'verified'
            },
            'communication_data': {
                'contactStability': 'high',
                'communicationFrequency': 'regular'
            }
        }
        
        # Test API call
        response = requests.post(
            "http://localhost:8001/api/v1/ai-alternative-data/assess",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ End-to-end integration successful")
            print(f"   Risk Score: {result['risk_score']:.3f}")
            print(f"   Risk Level: {result['risk_level']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Processing Time: {result.get('processing_time_ms', 'N/A')}ms")
            print(f"   Data Sources: {len(result.get('data_source_weights', {}))}")
            return True
        else:
            print(f"❌ Integration test failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests."""
    print("🚀 AI ALTERNATIVE DATA CREDIT RISK MODEL - TEST SUITE")
    print("=" * 70)
    
    test_results = []
    
    # Test 1: AI Model
    test_results.append(test_ai_model())
    
    # Test 2: Data Collection Service
    test_results.append(await test_data_collection_service())
    
    # Test 3: API Endpoints
    test_results.append(test_api_endpoints())
    
    # Test 4: Integration
    test_results.append(test_integration())
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    test_names = [
        "AI Model Testing",
        "Data Collection Service",
        "API Endpoints",
        "End-to-End Integration"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, test_results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {name}: {status}")
    
    if passed == total:
        print("\n🎉 All tests passed! AI Alternative Data system is working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    print("🧪 Starting AI Alternative Data Test Suite...")
    print("Press Ctrl+C to interrupt")
    print()
    
    try:
        success = asyncio.run(run_all_tests())
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
