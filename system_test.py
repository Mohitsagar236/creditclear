#!/usr/bin/env python3
"""
Comprehensive system test for the Credit Risk Model.

This script tests all major components to ensure everything is working correctly.
"""

import sys
import os
import importlib
import traceback
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add the mock middleware to Python path
mock_middleware_path = os.path.join(project_root, "src", "utils", "mock_middleware")
if os.path.exists(mock_middleware_path):
    sys.path.insert(0, mock_middleware_path)

def test_imports():
    """Test that all major modules can be imported."""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        'src.api.main',
        'src.models.base_model',
        'src.models.lightgbm_model', 
        'src.models.xgboost_model',
        'src.models.ensemble_model',
        'src.data_processing.feature_engineering',
        'src.data_processing.cleaners',
        'src.data_processing.collectors',
        'src.utils.config',
        'src.utils.logger',
        'src.utils.validators',
        'src.api.routes.predict',
        'src.api.routes.data_collection',
        'src.api.routes.device_analytics',
        'src.api.routes.comprehensive_data',
        'src.api.schemas.prediction',
        'src.api.schemas.device_data'
    ]
    
    results = []
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            results.append((module_name, True, None))
            print(f"  ✅ {module_name}")
        except Exception as e:
            results.append((module_name, False, str(e)))
            print(f"  ❌ {module_name}: {e}")
    
    return results

def test_model_classes():
    """Test that model classes can be instantiated."""
    print("\\n🤖 Testing model classes...")
    
    try:
        from src.models.lightgbm_model import LightGBMModel
        from src.models.xgboost_model import XGBoostModel
        from src.models.ensemble_model import EnsembleModel
        
        # Test LightGBM model
        lgb_model = LightGBMModel()
        print("  ✅ LightGBM model instantiated")
        
        # Test XGBoost model
        xgb_model = XGBoostModel()
        print("  ✅ XGBoost model instantiated")
        
        # Test Ensemble model
        ensemble_model = EnsembleModel()
        print("  ✅ Ensemble model instantiated")
        
        return True
    except Exception as e:
        print(f"  ❌ Model class test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\\n⚙️ Testing configuration loading...")
    
    try:
        from src.utils.config import get_config
        
        config = get_config()
        print(f"  ✅ Configuration loaded")
        print(f"  ✅ Database config: {config.database.host}:{config.database.port}")
        print(f"  ✅ API config: {config.api.host}:{config.api.port}")
        print(f"  ✅ Model config: Random state {config.model.random_state}")
        
        return True
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_validators():
    """Test validation utilities."""
    print("\\n✅ Testing validation utilities...")
    
    try:
        from src.utils.validators import InputValidator, CreditDataValidator, validate_prediction_input
        
        # Test phone validation
        phone_result = InputValidator.validate_phone_number("+919876543210")
        print(f"  ✅ Phone validation: {phone_result.is_valid}")
        
        # Test email validation
        email_result = InputValidator.validate_email("test@example.com")
        print(f"  ✅ Email validation: {email_result.is_valid}")
        
        # Test credit score validation
        score_result = CreditDataValidator.validate_credit_score(750)
        print(f"  ✅ Credit score validation: {score_result.is_valid}")
        
        # Test prediction input validation
        test_data = {
            'AMT_INCOME_TOTAL': 50000,
            'AMT_CREDIT': 200000,
            'CODE_GENDER': 'M'
        }
        pred_result = validate_prediction_input(test_data)
        print(f"  ✅ Prediction input validation: {pred_result.is_valid}")
        
        return True
    except Exception as e:
        print(f"  ❌ Validation test failed: {e}")
        traceback.print_exc()
        return False

def test_data_processing():
    """Test data processing utilities."""
    print("\\n📊 Testing data processing utilities...")
    
    try:
        from src.data_processing.feature_engineering import FeatureEngineer
        from src.data_processing.cleaners import DataCleaner
        import pandas as pd
        import numpy as np
        
        # Test feature engineering
        fe = FeatureEngineer()
        print("  ✅ FeatureEngineer instantiated")
        
        # Test data cleaner
        dc = DataCleaner()
        print("  ✅ DataCleaner instantiated")
        
        # Test with sample data
        sample_data = pd.DataFrame({
            'EXT_SOURCE_1': [0.5, 0.7, np.nan, 0.3],
            'EXT_SOURCE_2': [0.6, np.nan, 0.8, 0.4],
            'EXT_SOURCE_3': [np.nan, 0.9, 0.7, 0.5],
            'AMT_INCOME_TOTAL': [50000, 75000, 60000, 45000]
        })
        
        # Test polynomial features
        poly_data = fe.create_polynomial_features(sample_data)
        print(f"  ✅ Polynomial features created: {poly_data.shape}")
        
        # Test data cleaning
        cleaned_data = dc.impute_numerical(sample_data, ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3'])
        print(f"  ✅ Data cleaned: {cleaned_data.isnull().sum().sum()} missing values")
        
        return True
    except Exception as e:
        print(f"  ❌ Data processing test failed: {e}")
        traceback.print_exc()
        return False

def test_api_schemas():
    """Test API schemas."""
    print("\\n📋 Testing API schemas...")
    
    try:
        from src.api.schemas.prediction import PredictionRequest, PredictionResponse
        from src.api.schemas.device_data import MobileDeviceDataRequest
        
        # Test prediction request schema
        pred_data = {
            'AMT_INCOME_TOTAL': 50000.0,
            'AMT_CREDIT': 200000.0,
            'CODE_GENDER': 'M',
            'NAME_EDUCATION_TYPE': 'Higher education',
            'NAME_CONTRACT_TYPE': 'Cash loans',
            'FLAG_OWN_CAR': 'N',
            'FLAG_OWN_REALTY': 'Y',
            'CNT_CHILDREN': 0,
            'DAYS_BIRTH': -10000,  # Approx 27 years old in days
            'DAYS_EMPLOYED': -2000  # Approx 5.5 years employed in days
        }
        
        request = PredictionRequest(**pred_data)
        print("  ✅ PredictionRequest schema validated")
        
        # Test device data schema
        device_data = {
            'device_data': {
                'user_id': 'user-456',
                'device_info': {
                    'device_id': 'test-device-123',
                    'device_type': 'Smartphone',
                    'brand': 'Test Brand',
                    'manufacturer': 'Test Manufacturer',
                    'model': 'Test Model',
                    'device_name': 'Test Device',
                    'system_name': 'Android',
                    'system_version': '12.0',
                    'app_version': '1.0.0',
                    'build_version': '1.0.0',
                    'bundle_id': 'com.test.app',
                    'is_tablet': False,
                    'is_pin_or_fingerprint_set': True,
                    'platform': 'android',
                    'platform_version': '12.0'
                },
                'screen_info': {
                    'screen_width': 1080,
                    'screen_height': 2400,
                    'pixel_ratio': 3.0,
                    'window_width': 1080,
                    'window_height': 2400,
                    'font_scale': 1.0
                },
                'network_info': {
                    'type': 'wifi',
                    'is_connected': True,
                    'is_internet_reachable': True
                }
            }
        }
        
        device_request = MobileDeviceDataRequest(**device_data)
        print("  ✅ MobileDeviceDataRequest schema validated")
        
        return True
    except Exception as e:
        print(f"  ❌ API schema test failed: {e}")
        traceback.print_exc()
        return False

def test_logging():
    """Test logging utilities."""
    print("\\n📝 Testing logging utilities...")
    
    try:
        from src.utils.logger import get_logger, setup_logging
        
        # Setup logging
        setup_logging(log_level="INFO", enable_console=False)
        
        # Get logger
        logger = get_logger("test_logger")
        
        # Test logging methods
        logger.log_model_training("test_model", epochs=10, learning_rate=0.01)
        logger.log_data_collection("test_source", 100, quality="high")
        
        print("  ✅ Logging utilities working")
        
        return True
    except Exception as e:
        print(f"  ❌ Logging test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests."""
    print("🚀 Starting comprehensive system tests...\\n")
    
    test_results = []
    
    # Run all tests
    import_results = test_imports()
    test_results.append(("Import Tests", all(result[1] for result in import_results)))
    
    test_results.append(("Model Classes", test_model_classes()))
    test_results.append(("Configuration", test_config_loading()))
    test_results.append(("Validators", test_validators()))
    test_results.append(("Data Processing", test_data_processing()))
    test_results.append(("API Schemas", test_api_schemas()))
    test_results.append(("Logging", test_logging()))
    
    # Print summary
    print("\\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    
    for test_name, passed in test_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print("-"*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\\n🎉 ALL TESTS PASSED! System is ready for deployment.")
        return True
    else:
        print("\\n⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
