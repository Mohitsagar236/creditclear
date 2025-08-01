"""
Comprehensive AI Alternative Data Credit Risk Demo

This demo showcases the complete AI-powered credit risk assessment system
that automatically detects and analyzes alternative data from user devices
and integrates it with traditional Kaggle data for enhanced risk prediction.
"""

import asyncio
import json
import logging
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.ai_alternative_data_model import AIAlternativeDataModel
from src.services.automatic_data_collection import AutomaticDataCollectionService
from src.utils.data_loader import load_kaggle_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIAlternativeDataDemo:
    """Comprehensive demo for AI Alternative Data Credit Risk Assessment."""
    
    def __init__(self):
        """Initialize the demo."""
        self.ai_model = AIAlternativeDataModel()
        self.data_service = AutomaticDataCollectionService()
        self.demo_users = self._create_demo_users()
        
    def _create_demo_users(self) -> Dict[str, Dict[str, Any]]:
        """Create diverse demo user profiles for testing."""
        return {
            'user_low_risk': {
                'profile': 'Low Risk Profile - Stable Employment, Good Device',
                'kaggle_data': {
                    'AMT_INCOME_TOTAL': 250000,  # High income
                    'AMT_CREDIT': 300000,
                    'AMT_ANNUITY': 15000,
                    'DAYS_BIRTH': -12000,  # ~33 years old
                    'DAYS_EMPLOYED': -3650,  # 10 years employed
                    'CNT_FAM_MEMBERS': 2,
                    'NAME_CONTRACT_TYPE': 'Cash loans',
                    'CODE_GENDER': 'F',
                    'FLAG_OWN_CAR': 'Y',
                    'FLAG_OWN_REALTY': 'Y',
                    'NAME_INCOME_TYPE': 'Working',
                    'NAME_EDUCATION_TYPE': 'Higher education',
                    'NAME_FAMILY_STATUS': 'Married',
                    'NAME_HOUSING_TYPE': 'House / apartment',
                    'EXT_SOURCE_1': 0.8,
                    'EXT_SOURCE_2': 0.75,
                    'EXT_SOURCE_3': 0.85
                },
                'device_data': {
                    'device': {
                        'model': 'iPhone 14 Pro',
                        'platform': 'iOS',
                        'systemVersion': '16.4',
                        'isPinOrFingerprintSet': True,
                        'totalMemory': 6442450944,  # 6GB
                        'totalDiskCapacity': 256849018880,  # 256GB
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
                        'totalCount': 12,
                        'banking': ['SBI', 'ICICI', 'HDFC'],
                        'investment': ['Zerodha', 'Groww'],
                        'lending': []
                    }
                },
                'alternative_data': {
                    'location': {
                        'currentCity': 'Mumbai',
                        'homeLocation': 'detected',
                        'workLocation': 'detected',
                        'travelPatterns': 'regular_commuter'
                    },
                    'utility': {
                        'mobileRecharge': 'regular',
                        'electricityBill': 'consistent',
                        'internetUsage': 'high',
                        'subscriptionServices': 'multiple'
                    },
                    'digitalFootprint': {
                        'socialMediaPresence': 'professional',
                        'onlineActivity': 'regular',
                        'digitalIdentity': 'verified'
                    },
                    'communication': {
                        'contactStability': 'high',
                        'communicationFrequency': 'regular'
                    }
                }
            },
            
            'user_medium_risk': {
                'profile': 'Medium Risk Profile - Moderate Income, Some Risk Factors',
                'kaggle_data': {
                    'AMT_INCOME_TOTAL': 120000,  # Moderate income
                    'AMT_CREDIT': 400000,
                    'AMT_ANNUITY': 22000,
                    'DAYS_BIRTH': -8000,  # ~22 years old
                    'DAYS_EMPLOYED': -730,  # 2 years employed
                    'CNT_FAM_MEMBERS': 3,
                    'NAME_CONTRACT_TYPE': 'Cash loans',
                    'CODE_GENDER': 'M',
                    'FLAG_OWN_CAR': 'N',
                    'FLAG_OWN_REALTY': 'N',
                    'NAME_INCOME_TYPE': 'Working',
                    'NAME_EDUCATION_TYPE': 'Secondary / secondary special',
                    'NAME_FAMILY_STATUS': 'Single / not married',
                    'NAME_HOUSING_TYPE': 'Rented apartment',
                    'EXT_SOURCE_1': 0.5,
                    'EXT_SOURCE_2': 0.6,
                    'EXT_SOURCE_3': 0.4
                },
                'device_data': {
                    'device': {
                        'model': 'Samsung Galaxy A52',
                        'platform': 'Android',
                        'systemVersion': '12.0',
                        'isPinOrFingerprintSet': True,
                        'totalMemory': 4294967296,  # 4GB
                        'totalDiskCapacity': 64424509440,  # 64GB
                        'isTablet': False
                    },
                    'network': {
                        'type': 'cellular',
                        'isConnected': True,
                        'isInternetReachable': True,
                        'details': {'isConnectionExpensive': True}
                    },
                    'riskFlags': {
                        'isEmulator': False,
                        'isRooted': False,
                        'isJailbroken': False,
                        'hasSecurityFeatures': True,
                        'isDebuggingEnabled': False
                    },
                    'apps': {
                        'totalCount': 6,
                        'banking': ['PhonePe', 'GooglePay'],
                        'investment': [],
                        'lending': ['Paytm']
                    }
                },
                'alternative_data': {
                    'location': {
                        'currentCity': 'Pune',
                        'homeLocation': 'detected',
                        'workLocation': 'partial',
                        'travelPatterns': 'occasional_travel'
                    },
                    'utility': {
                        'mobileRecharge': 'irregular',
                        'electricityBill': 'delayed_sometimes',
                        'internetUsage': 'medium',
                        'subscriptionServices': 'single'
                    },
                    'digitalFootprint': {
                        'socialMediaPresence': 'moderate',
                        'onlineActivity': 'occasional',
                        'digitalIdentity': 'partial'
                    },
                    'communication': {
                        'contactStability': 'medium',
                        'communicationFrequency': 'moderate'
                    }
                }
            },
            
            'user_high_risk': {
                'profile': 'High Risk Profile - Low Income, Security Issues',
                'kaggle_data': {
                    'AMT_INCOME_TOTAL': 80000,  # Low income
                    'AMT_CREDIT': 500000,  # High credit amount relative to income
                    'AMT_ANNUITY': 35000,
                    'DAYS_BIRTH': -7000,  # ~19 years old
                    'DAYS_EMPLOYED': -180,  # 6 months employed
                    'CNT_FAM_MEMBERS': 4,
                    'NAME_CONTRACT_TYPE': 'Cash loans',
                    'CODE_GENDER': 'M',
                    'FLAG_OWN_CAR': 'N',
                    'FLAG_OWN_REALTY': 'N',
                    'NAME_INCOME_TYPE': 'Working',
                    'NAME_EDUCATION_TYPE': 'Lower secondary',
                    'NAME_FAMILY_STATUS': 'Single / not married',
                    'NAME_HOUSING_TYPE': 'With parents',
                    'EXT_SOURCE_1': 0.2,
                    'EXT_SOURCE_2': 0.3,
                    'EXT_SOURCE_3': 0.1
                },
                'device_data': {
                    'device': {
                        'model': 'Generic Android',
                        'platform': 'Android',
                        'systemVersion': '8.0',  # Outdated
                        'isPinOrFingerprintSet': False,
                        'totalMemory': 2147483648,  # 2GB
                        'totalDiskCapacity': 16106127360,  # 16GB
                        'isTablet': False
                    },
                    'network': {
                        'type': 'cellular',
                        'isConnected': True,
                        'isInternetReachable': False,  # Poor connection
                        'details': {'isConnectionExpensive': True}
                    },
                    'riskFlags': {
                        'isEmulator': True,  # High risk
                        'isRooted': True,    # High risk
                        'isJailbroken': False,
                        'hasSecurityFeatures': False,
                        'isDebuggingEnabled': True  # Risk factor
                    },
                    'apps': {
                        'totalCount': 2,
                        'banking': [],
                        'investment': [],
                        'lending': ['EarlySalary', 'MoneyTap']  # Multiple lending apps
                    }
                },
                'alternative_data': {
                    'location': {
                        'currentCity': 'Unknown',
                        'homeLocation': 'not_detected',
                        'workLocation': 'not_detected',
                        'travelPatterns': 'nomadic'
                    },
                    'utility': {
                        'mobileRecharge': 'irregular',
                        'electricityBill': 'frequently_delayed',
                        'internetUsage': 'low',
                        'subscriptionServices': 'none'
                    },
                    'digitalFootprint': {
                        'socialMediaPresence': 'limited',
                        'onlineActivity': 'minimal',
                        'digitalIdentity': 'unverified'
                    },
                    'communication': {
                        'contactStability': 'low',
                        'communicationFrequency': 'sporadic'
                    }
                }
            }
        }
    
    async def run_comprehensive_demo(self):
        """Run the complete AI alternative data demo."""
        print("=" * 80)
        print("🤖 AI ALTERNATIVE DATA CREDIT RISK ASSESSMENT DEMO")
        print("=" * 80)
        print()
        
        # Initialize the service
        print("📊 Initializing AI Alternative Data Service...")
        await self.data_service.initialize_service()
        
        if not self.data_service.ai_model.is_fitted:
            print("🔧 Training AI model with Kaggle data...")
            await self._train_model()
        
        print("✅ Service initialization complete!")
        print()
        
        # Process each demo user
        for user_id, user_data in self.demo_users.items():
            await self._process_demo_user(user_id, user_data)
            print()
        
        # Show model information
        await self._show_model_information()
        
        # Performance summary
        await self._show_performance_summary()
    
    async def _train_model(self):
        """Train the AI model with sample data."""
        try:
            # Create training data with diverse profiles
            training_data = []
            labels = []
            
            # Generate synthetic training data based on demo profiles
            for i in range(1000):
                if i % 3 == 0:
                    # Low risk samples
                    base_data = self.demo_users['user_low_risk']['kaggle_data'].copy()
                    # Add some variation
                    base_data['AMT_INCOME_TOTAL'] *= (0.8 + 0.4 * (i % 10) / 10)
                    training_data.append(base_data)
                    labels.append(0)  # No default
                elif i % 3 == 1:
                    # Medium risk samples
                    base_data = self.demo_users['user_medium_risk']['kaggle_data'].copy()
                    base_data['AMT_INCOME_TOTAL'] *= (0.8 + 0.4 * (i % 10) / 10)
                    training_data.append(base_data)
                    labels.append(0 if i % 4 != 0 else 1)  # 25% default rate
                else:
                    # High risk samples
                    base_data = self.demo_users['user_high_risk']['kaggle_data'].copy()
                    base_data['AMT_INCOME_TOTAL'] *= (0.8 + 0.4 * (i % 10) / 10)
                    training_data.append(base_data)
                    labels.append(1 if i % 2 == 0 else 0)  # 50% default rate
            
            # Convert to DataFrame
            training_df = pd.DataFrame(training_data)
            
            # Prepare alternative data features for training
            device_features = self.ai_model.extract_device_features(
                self.demo_users['user_low_risk']['device_data']
            )
            behavioral_features = self.ai_model.extract_behavioral_features(
                self.demo_users['user_low_risk']['alternative_data']
            )
            
            # Preprocess and combine features
            processed_kaggle = self.ai_model.preprocess_kaggle_data(training_df)
            combined_features = self.ai_model.combine_features(
                processed_kaggle, device_features, behavioral_features
            )
            
            # Train the model
            self.ai_model.fit(combined_features, pd.Series(labels))
            print("✅ AI model training completed successfully!")
            
        except Exception as e:
            print(f"❌ Error training model: {e}")
    
    async def _process_demo_user(self, user_id: str, user_data: Dict[str, Any]):
        """Process a single demo user through the complete pipeline."""
        print(f"👤 Processing Demo User: {user_id}")
        print(f"📋 Profile: {user_data['profile']}")
        print("-" * 60)
        
        # Step 1: Automatic data collection
        print("🔍 Step 1: Automatic Alternative Data Collection")
        device_profile = user_data['device_data']
        
        collected_data = await self.data_service.collect_comprehensive_data(user_id, device_profile)
        
        print(f"   📊 Data Quality Score: {collected_data['overall_quality_score']:.2f}/100")
        print(f"   ✅ Collection Status: {collected_data['collection_status'].upper()}")
        print(f"   📦 Data Sources: {len(collected_data['data_sources'])}")
        
        # Step 2: AI Risk Assessment
        print("\n🤖 Step 2: AI-Powered Risk Assessment")
        
        # Override collected data with demo data for consistent results
        collected_data['data_sources']['kaggle_features'] = user_data['kaggle_data']
        collected_data['data_sources']['device_analytics'] = user_data['device_data']
        collected_data['data_sources']['location_data'] = user_data['alternative_data']['location']
        collected_data['data_sources']['utility_data'] = user_data['alternative_data']['utility']
        collected_data['data_sources']['digital_footprint'] = user_data['alternative_data']['digitalFootprint']
        collected_data['data_sources']['communication_data'] = user_data['alternative_data']['communication']
        
        assessment_result = await self.data_service.perform_ai_risk_assessment(collected_data)
        
        # Step 3: Display Results
        print(f"   🎯 Risk Score: {assessment_result['risk_score']:.3f}/1.000")
        print(f"   📊 Risk Level: {assessment_result['risk_level'].upper()}")
        print(f"   🎯 Confidence: {assessment_result['confidence']:.2%}")
        
        print("\n   🧠 Model Component Scores:")
        for model_name, score in assessment_result['model_scores'].items():
            print(f"      • {model_name.replace('_', ' ').title()}: {score:.3f}")
        
        print("\n   💡 Key Insights:")
        for insight in assessment_result['insights'][:3]:  # Show top 3 insights
            print(f"      {insight}")
        
        print("\n   📋 Recommendations:")
        for recommendation in assessment_result['recommendations'][:3]:  # Show top 3 recommendations
            print(f"      • {recommendation}")
        
        # Show data source contributions
        print("\n   📊 Data Source Weights:")
        for source, weight in assessment_result['data_source_weights'].items():
            print(f"      • {source.title()}: {weight:.2%}")
        
        # Show top feature contributions
        print("\n   🔍 Top Feature Contributions:")
        for i, (feature, contribution) in enumerate(list(assessment_result['feature_contributions'].items())[:5]):
            print(f"      {i+1}. {feature}: {contribution:.3f}")
    
    async def _show_model_information(self):
        """Display comprehensive model information."""
        print("🔬 AI MODEL INFORMATION")
        print("-" * 60)
        
        model_info = self.ai_model.get_model_info()
        
        print(f"Model Type: {model_info['model_type']}")
        print(f"Features: {model_info['feature_count']}")
        print(f"Data Sources: {', '.join(model_info['data_sources'])}")
        print(f"Algorithms: {', '.join(model_info['algorithms'])}")
        
        print("\nCapabilities:")
        for capability in model_info['capabilities']:
            print(f"  • {capability}")
        
        print(f"\nRisk Thresholds:")
        for level, threshold in model_info['risk_thresholds'].items():
            print(f"  • {level.title()}: ≤ {threshold}")
    
    async def _show_performance_summary(self):
        """Show performance summary and statistics."""
        print("📈 PERFORMANCE SUMMARY")
        print("-" * 60)
        
        # Calculate summary statistics
        demo_results = []
        for user_id, user_data in self.demo_users.items():
            # Quick assessment for summary
            kaggle_df = pd.DataFrame([user_data['kaggle_data']])
            assessment = self.ai_model.predict_comprehensive_risk(
                kaggle_data=kaggle_df,
                device_data=user_data['device_data'],
                alternative_data=user_data['alternative_data']
            )
            demo_results.append({
                'user': user_id,
                'risk_score': assessment['risk_score'],
                'risk_level': assessment['risk_level'],
                'confidence': assessment['confidence']
            })
        
        print(f"Total Users Processed: {len(demo_results)}")
        print(f"Average Risk Score: {sum(r['risk_score'] for r in demo_results) / len(demo_results):.3f}")
        print(f"Average Confidence: {sum(r['confidence'] for r in demo_results) / len(demo_results):.2%}")
        
        print("\nRisk Distribution:")
        risk_counts = {}
        for result in demo_results:
            risk_level = result['risk_level']
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        for risk_level, count in risk_counts.items():
            percentage = (count / len(demo_results)) * 100
            print(f"  • {risk_level}: {count} users ({percentage:.1f}%)")
        
        print("\n🎉 Demo completed successfully!")
        print("=" * 80)


async def main():
    """Main demo execution function."""
    try:
        demo = AIAlternativeDataDemo()
        await demo.run_comprehensive_demo()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Starting AI Alternative Data Credit Risk Demo...")
    print("Press Ctrl+C to interrupt at any time")
    print()
    
    # Run the async demo
    asyncio.run(main())
