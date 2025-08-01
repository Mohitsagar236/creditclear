#!/usr/bin/env python3
"""
Test script for device features in the FeatureEngineer class.

This script demonstrates how to use the create_device_features method
with realistic device and app usage data for credit risk assessment.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from data_processing.feature_engineering import FeatureEngineer
    print("✅ Successfully imported FeatureEngineer")
except ImportError as e:
    print(f"❌ Failed to import FeatureEngineer: {e}")
    print("Please ensure you're running this from the project root directory")
    sys.exit(1)

def generate_realistic_device_data(n_users=5):
    """
    Generate realistic device and app usage data for testing device features.
    
    Args:
        n_users: Number of users to generate data for
    
    Returns:
        DataFrame with device and app usage data
    """
    np.random.seed(42)
    
    device_data = []
    
    # Device models with different characteristics
    device_models = [
        'iPhone 14 Pro', 'iPhone 13', 'iPhone 12', 'iPhone SE',
        'Samsung Galaxy S23', 'Samsung Galaxy A54', 'Samsung Galaxy S22',
        'Google Pixel 7', 'Google Pixel 6a', 'OnePlus 11',
        'Xiaomi 13', 'Huawei P50'
    ]
    
    # Realistic app combinations by user profile
    app_profiles = {
        'financial_professional': [
            'Chase Mobile', 'Bank of America', 'Wells Fargo Mobile', 'PayPal',
            'Venmo', 'Mint', 'Robinhood', 'TD Ameritrade', 'QuickBooks',
            'Microsoft Office', 'LinkedIn', 'Slack', 'Norton Security',
            'LastPass', 'Google Authenticator'
        ],
        'tech_savvy': [
            'Coinbase', 'Crypto.com', 'MetaMask', 'Discord', 'GitHub',
            'Stack Overflow', 'Bitwarden', 'NordVPN', 'Authy',
            'Google Drive', 'Dropbox', 'Adobe Creative', 'Figma'
        ],
        'casual_user': [
            'Venmo', 'Cash App', 'Zelle', 'Facebook', 'Instagram',
            'TikTok', 'Netflix', 'Spotify', 'Uber', 'DoorDash',
            'Amazon', 'Target', 'Walmart'
        ],
        'security_conscious': [
            'Bank of America', 'Capital One', 'Credit Karma', 'Experian',
            'Norton 360', 'McAfee Mobile Security', '1Password', 'Signal',
            'ProtonMail', 'DuckDuckGo', 'VPN Unlimited', 'Malwarebytes'
        ],
        'business_owner': [
            'QuickBooks Self-Employed', 'Square', 'PayPal Business',
            'American Express', 'Chase Business', 'FreshBooks',
            'Microsoft Teams', 'Zoom', 'DocuSign', 'Google Workspace',
            'Salesforce', 'HubSpot', 'Kaspersky Security'
        ]
    }
    
    user_profiles = list(app_profiles.keys())
    
    for user_id in range(1, n_users + 1):
        # Select device model
        device_model = np.random.choice(device_models)
        
        # Generate usage patterns based on device tier
        is_premium = any(premium in device_model for premium in 
                        ['Pro', 'Ultra', 'OnePlus', 'Pixel 7'])
        
        # User profile affects app choices and usage
        user_profile = np.random.choice(user_profiles)
        base_apps = app_profiles[user_profile].copy()
        
        # Add some random apps from other profiles
        other_profiles = [p for p in user_profiles if p != user_profile]
        for _ in range(np.random.randint(2, 6)):
            other_profile = np.random.choice(other_profiles)
            if app_profiles[other_profile]:
                base_apps.append(np.random.choice(app_profiles[other_profile]))
        
        # Remove duplicates
        installed_apps = list(set(base_apps))
        
        # Data usage patterns
        if is_premium:
            # Premium device users tend to use more data
            daily_data_mb = np.random.normal(1200, 400)
            wifi_data_mb = np.random.normal(25000, 8000)  # Monthly WiFi
            cellular_data_mb = np.random.normal(8000, 3000)  # Monthly cellular
        else:
            daily_data_mb = np.random.normal(800, 300)
            wifi_data_mb = np.random.normal(15000, 5000)
            cellular_data_mb = np.random.normal(5000, 2000)
        
        # Ensure positive values
        daily_data_mb = max(100, daily_data_mb)
        wifi_data_mb = max(1000, wifi_data_mb)
        cellular_data_mb = max(500, cellular_data_mb)
        
        # Financial and security conscious users have different patterns
        if user_profile in ['financial_professional', 'security_conscious']:
            # More WiFi usage (cost conscious)
            wifi_data_mb *= np.random.uniform(1.2, 1.5)
            cellular_data_mb *= np.random.uniform(0.7, 0.9)
        elif user_profile == 'business_owner':
            # Higher overall usage
            daily_data_mb *= np.random.uniform(1.3, 1.6)
            cellular_data_mb *= np.random.uniform(1.2, 1.4)
        
        device_data.append({
            'SK_ID_CURR': user_id,
            'device_model': device_model,
            'installed_apps': ', '.join(installed_apps),
            'daily_data_usage_mb': round(daily_data_mb, 1),
            'wifi_data_mb': round(wifi_data_mb, 1),
            'cellular_data_mb': round(cellular_data_mb, 1),
            'user_profile': user_profile  # For reference, normally not available
        })
    
    return pd.DataFrame(device_data)

def main():
    """Main function to test device features."""
    print("📱 Testing Device Features")
    print("=" * 50)
    
    # Generate test data
    print("📊 Generating realistic device and app usage data...")
    device_data = generate_realistic_device_data(n_users=5)
    print(f"   Generated device data for {len(device_data)} users")
    
    # Create sample credit application data
    credit_data = pd.DataFrame({
        'SK_ID_CURR': [1, 2, 3, 4, 5],
        'NAME_CONTRACT_TYPE': ['Cash loans', 'Cash loans', 'Revolving loans', 'Cash loans', 'Cash loans'],
        'AMT_CREDIT': [500000, 300000, 150000, 750000, 200000],
        'AMT_INCOME_TOTAL': [180000, 120000, 90000, 250000, 100000]
    })
    
    print(f"📋 Credit application data:")
    print(credit_data)
    print()
    
    print(f"📱 Device data sample:")
    for idx, row in device_data.iterrows():
        apps = row['installed_apps'].split(', ')
        print(f"   👤 User {row['SK_ID_CURR']}: {row['device_model']} | {len(apps)} apps | {row['daily_data_usage_mb']:.0f} MB/day")
    print()
    
    # Initialize FeatureEngineer
    engineer = FeatureEngineer()
    
    try:
        print("🔧 Creating device features...")
        enhanced_data = engineer.create_device_features(
            df=credit_data,
            device_data=device_data,
            user_id_col='SK_ID_CURR',
            device_model_col='device_model',
            app_list_col='installed_apps',
            daily_data_col='daily_data_usage_mb',
            wifi_data_col='wifi_data_mb',
            cellular_data_col='cellular_data_mb'
        )
        
        print("✅ Device features created successfully!")
        print()
        
        # Display device features
        device_cols = [col for col in enhanced_data.columns 
                      if col not in credit_data.columns]
        
        print("📊 DEVICE FEATURES SUMMARY:")
        print("-" * 80)
        
        for user_id in enhanced_data['SK_ID_CURR']:
            user_features = enhanced_data[enhanced_data['SK_ID_CURR'] == user_id].iloc[0]
            user_device = device_data[device_data['SK_ID_CURR'] == user_id].iloc[0]
            
            print(f"\n👤 USER {user_id} - Device Analysis:")
            print(f"   📱 Device: {user_device['device_model']}")
            print(f"   📅 Device Age: {user_features['device_age_months']:.1f} months")
            print(f"   ⭐ Generation Score: {user_features['device_generation_score']}/5")
            print(f"   💎 Premium Device: {'Yes' if user_features['is_premium_device'] else 'No'}")
            print(f"   💰 Value Tier: {user_features['device_value_tier']}/5")
            print(f"   💳 Financial Apps: {user_features['financial_apps_count']}")
            print(f"   🔒 Security Apps: {user_features['security_apps_count']}")
            print(f"   📈 App Sophistication: {user_features['app_sophistication_score']:.1f}/10")
            print(f"   📊 Daily Data: {user_features['avg_daily_data_mb']:.0f} MB")
            print(f"   📶 WiFi/Cellular Ratio: {user_features['wifi_cellular_ratio']:.2f}")
            print(f"   🏆 Network Efficiency: {user_features['network_efficiency_score']}/5")
        
        print("\n" + "=" * 80)
        print("🎯 DEVICE-BASED CREDIT RISK INSIGHTS:")
        print("=" * 80)
        
        for user_id in enhanced_data['SK_ID_CURR']:
            user_features = enhanced_data[enhanced_data['SK_ID_CURR'] == user_id].iloc[0]
            user_device = device_data[device_data['SK_ID_CURR'] == user_id].iloc[0]
            
            # Device-based risk assessment
            risk_factors = []
            risk_score = 0
            
            # Device age and value
            if user_features['device_age_months'] > 36:
                risk_factors.append("Old device")
                risk_score += 1
            
            if user_features['is_premium_device'] == 0 and user_features['device_value_tier'] <= 2:
                risk_factors.append("Low-value device")
                risk_score += 1
            else:
                risk_score -= 1  # Premium devices reduce risk
            
            # Financial app sophistication
            if user_features['financial_apps_count'] >= 3:
                risk_factors.append("High financial app usage")
                risk_score -= 1  # Positive indicator
            elif user_features['financial_apps_count'] == 0:
                risk_factors.append("No financial apps")
                risk_score += 1
            
            # Security awareness
            if user_features['security_apps_count'] >= 2:
                risk_score -= 0.5  # Security conscious
            elif user_features['security_apps_count'] == 0:
                risk_factors.append("No security apps")
                risk_score += 0.5
            
            # Data usage patterns
            if user_features['data_usage_tier'] >= 4:
                risk_score -= 0.5  # Heavy usage suggests engagement
            elif user_features['data_usage_tier'] <= 2:
                risk_factors.append("Low data usage")
                risk_score += 0.5
            
            # Network efficiency (cost consciousness)
            if user_features['network_efficiency_score'] >= 4:
                risk_score -= 0.5  # Cost conscious
            elif user_features['network_efficiency_score'] <= 2:
                risk_factors.append("Poor network efficiency")
                risk_score += 0.5
            
            # Overall app sophistication
            if user_features['app_sophistication_score'] >= 7:
                risk_score -= 1  # Tech-savvy, financially engaged
            elif user_features['app_sophistication_score'] <= 3:
                risk_factors.append("Low app sophistication")
                risk_score += 1
            
            # Determine risk level
            if risk_score <= -1:
                risk_level = "LOW"
                risk_desc = "Device patterns suggest financial stability and tech engagement"
            elif risk_score <= 1:
                risk_level = "MEDIUM"
                risk_desc = "Mixed device indicators, moderate risk"
            else:
                risk_level = "HIGH"
                risk_desc = "Device patterns suggest potential financial constraints"
            
            print(f"\n👤 USER {user_id} Risk Assessment:")
            print(f"   📊 Risk Level: {risk_level}")
            print(f"   🎯 Risk Score: {risk_score:.1f}")
            print(f"   💡 Description: {risk_desc}")
            print(f"   📱 Profile: {user_device['user_profile']}")
            if risk_factors:
                print(f"   ⚠️  Risk Factors: {', '.join(risk_factors)}")
            else:
                print(f"   ✅ No significant risk factors identified")
        
        print("\n📈 DEVICE FEATURE IMPORTANCE:")
        print("-" * 60)
        
        feature_insights = {
            'device_age_months': 'Newer devices suggest better financial status',
            'is_premium_device': 'Premium devices indicate higher disposable income',
            'financial_apps_count': 'Financial engagement shows creditworthiness awareness',
            'security_apps_count': 'Security consciousness indicates responsible behavior',
            'app_sophistication_score': 'Tech sophistication correlates with financial literacy',
            'wifi_cellular_ratio': 'WiFi preference shows cost consciousness',
            'network_efficiency_score': 'Efficient usage patterns suggest financial planning',
            'data_usage_tier': 'Moderate-high usage indicates engagement and income'
        }
        
        for feature, insight in feature_insights.items():
            avg_val = enhanced_data[feature].mean()
            print(f"   📊 {feature:.<30} {insight}")
            print(f"      {'':.<30} Average: {avg_val:.2f}")
        
        print("\n📋 Feature Statistics:")
        print("-" * 50)
        for col in device_cols:
            values = enhanced_data[col]
            print(f"{col:.<35} {values.mean():.3f} ± {values.std():.3f}")
        
    except Exception as e:
        print(f"❌ Error creating device features: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ Device features test completed successfully!")
    print("\n💡 Integration Notes:")
    print("   - Device model lookup table requires periodic updates")
    print("   - App categorization can be enhanced with ML classification")
    print("   - Privacy considerations for app usage data collection")
    print("   - Device features complement traditional credit scoring")
    print("   - Network behavior reveals cost consciousness and lifestyle")

if __name__ == "__main__":
    main()
