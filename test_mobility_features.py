#!/usr/bin/env python3
"""
Test script for mobility features in the FeatureEngineer class.

This script demonstrates how to use the create_mobility_features method
with realistic GPS trajectory data for credit risk assessment.
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

def generate_realistic_gps_data(n_users=5, days=30):
    """
    Generate realistic GPS trajectory data for testing mobility features.
    
    Args:
        n_users: Number of users to generate data for
        days: Number of days of GPS data per user
    
    Returns:
        DataFrame with GPS trajectory data
    """
    np.random.seed(42)
    
    gps_data = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Base locations (Beijing coordinates similar to real Geolife dataset)
    base_locations = {
        'home': [39.9042, 116.4074],
        'work': [39.9388, 116.3974],
        'shopping': [39.9170, 116.3972],
        'restaurant': [39.9280, 116.4100]
    }
    
    # Cellular towers and WiFi networks
    towers = [f"TOWER_{i:03d}" for i in range(10)]
    networks = [f"WiFi_{name}" for name in ['Home', 'Office', 'Starbucks', 'Mall', 'Restaurant']]
    
    for user_id in range(1, n_users + 1):
        # Each user has their own slight variation of home/work locations
        user_home = [
            base_locations['home'][0] + np.random.normal(0, 0.01),
            base_locations['home'][1] + np.random.normal(0, 0.01)
        ]
        user_work = [
            base_locations['work'][0] + np.random.normal(0, 0.008),
            base_locations['work'][1] + np.random.normal(0, 0.008)
        ]
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            
            # Generate hourly GPS points
            for hour in range(24):
                # Generate multiple points per hour with some randomness
                points_per_hour = np.random.poisson(3) + 1  # 1-6 points per hour
                
                for point in range(points_per_hour):
                    timestamp = current_date + timedelta(
                        hours=hour, 
                        minutes=np.random.randint(0, 60),
                        seconds=np.random.randint(0, 60)
                    )
                    
                    # Determine location based on time and user behavior
                    if 22 <= hour or hour <= 6:  # Night time - at home
                        lat = user_home[0] + np.random.normal(0, 0.0005)
                        lon = user_home[1] + np.random.normal(0, 0.0005)
                        tower = towers[0] if np.random.random() > 0.1 else np.random.choice(towers[:3])
                        network = networks[0] if np.random.random() > 0.15 else None
                        
                    elif 9 <= hour <= 17:  # Work hours
                        lat = user_work[0] + np.random.normal(0, 0.0003)
                        lon = user_work[1] + np.random.normal(0, 0.0003)
                        tower = towers[1] if np.random.random() > 0.1 else np.random.choice(towers[1:4])
                        network = networks[1] if np.random.random() > 0.2 else None
                        
                    elif 7 <= hour <= 8 or 18 <= hour <= 19:  # Commute time
                        # Interpolate between home and work
                        ratio = np.random.random()
                        lat = user_home[0] * (1-ratio) + user_work[0] * ratio + np.random.normal(0, 0.002)
                        lon = user_home[1] * (1-ratio) + user_work[1] * ratio + np.random.normal(0, 0.002)
                        tower = np.random.choice(towers[:6])
                        network = None if np.random.random() > 0.3 else np.random.choice(networks[2:])
                        
                    else:  # Other activities
                        if np.random.random() < 0.3:  # Shopping/dining
                            location = np.random.choice(['shopping', 'restaurant'])
                            lat = base_locations[location][0] + np.random.normal(0, 0.001)
                            lon = base_locations[location][1] + np.random.normal(0, 0.001)
                            tower = np.random.choice(towers[2:8])
                            network = np.random.choice(networks[2:]) if np.random.random() > 0.4 else None
                        else:  # Near home
                            lat = user_home[0] + np.random.normal(0, 0.003)
                            lon = user_home[1] + np.random.normal(0, 0.003)
                            tower = towers[0] if np.random.random() > 0.2 else np.random.choice(towers[:4])
                            network = networks[0] if np.random.random() > 0.3 else None
                    
                    gps_data.append({
                        'SK_ID_CURR': user_id,
                        'timestamp': timestamp,
                        'latitude': lat,
                        'longitude': lon,
                        'tower_id': tower,
                        'network_id': network
                    })
    
    return pd.DataFrame(gps_data)

def main():
    """Main function to test mobility features."""
    print("🗺️ Testing Mobility Features")
    print("=" * 50)
    
    # Generate test data
    print("📊 Generating realistic GPS trajectory data...")
    gps_data = generate_realistic_gps_data(n_users=3, days=30)
    print(f"   Generated {len(gps_data)} GPS points for {gps_data['SK_ID_CURR'].nunique()} users")
    
    # Create sample credit application data
    credit_data = pd.DataFrame({
        'SK_ID_CURR': [1, 2, 3],
        'NAME_CONTRACT_TYPE': ['Cash loans', 'Cash loans', 'Revolving loans'],
        'AMT_CREDIT': [500000, 300000, 150000],
        'AMT_INCOME_TOTAL': [180000, 120000, 90000]
    })
    
    print(f"📋 Credit application data:")
    print(credit_data)
    print()
    
    # Initialize FeatureEngineer
    engineer = FeatureEngineer()
    
    try:
        print("🔧 Creating mobility features...")
        enhanced_data = engineer.create_mobility_features(
            df=credit_data,
            gps_data=gps_data,
            user_id_col='SK_ID_CURR',
            timestamp_col='timestamp',
            latitude_col='latitude',
            longitude_col='longitude',
            tower_id_col='tower_id',
            network_id_col='network_id'
        )
        
        print("✅ Mobility features created successfully!")
        print()
        
        # Display mobility features
        mobility_cols = [col for col in enhanced_data.columns 
                        if col not in credit_data.columns]
        
        print("📊 MOBILITY FEATURES SUMMARY:")
        print("-" * 80)
        
        for user_id in enhanced_data['SK_ID_CURR']:
            user_features = enhanced_data[enhanced_data['SK_ID_CURR'] == user_id].iloc[0]
            
            print(f"\n👤 USER {user_id} - Mobility Analysis:")
            print(f"   🏠 Home Location: ({user_features['home_location_lat']:.6f}, {user_features['home_location_lon']:.6f})")
            print(f"   🏢 Work Location: ({user_features['work_location_lat']:.6f}, {user_features['work_location_lon']:.6f})")
            print(f"   📏 Commute Distance: {user_features['home_work_distance_km']:.2f} km")
            print(f"   📡 Unique Towers: {user_features['unique_towers_count']}")
            print(f"   📶 Unique Networks: {user_features['unique_networks_count']}")
            print(f"   🎯 Location Stability: {user_features['location_stability_score']:.3f}")
            print(f"   🚗 Commute Consistency: {user_features['commute_consistency_score']:.3f}")
            print(f"   📍 Travel Radius (95th): {user_features['mobility_range_95th_percentile']:.2f} km")
            print(f"   🌍 Geographic Spread: {user_features['geographic_spread']:.6f}")
            print(f"   📈 Movement Entropy: {user_features['movement_entropy']:.3f}")
        
        print("\n" + "=" * 80)
        print("🎯 CREDIT RISK INSIGHTS:")
        print("=" * 80)
        
        for user_id in enhanced_data['SK_ID_CURR']:
            user_features = enhanced_data[enhanced_data['SK_ID_CURR'] == user_id].iloc[0]
            
            # Simple risk assessment based on mobility patterns
            risk_factors = []
            risk_score = 0
            
            # Long commute risk
            if user_features['home_work_distance_km'] > 20:
                risk_factors.append("Very long commute")
                risk_score += 2
            elif user_features['home_work_distance_km'] > 10:
                risk_factors.append("Long commute")
                risk_score += 1
            
            # Location instability
            if user_features['location_stability_score'] < 0.3:
                risk_factors.append("Low location stability")
                risk_score += 1
            
            # High mobility
            if user_features['mobility_range_95th_percentile'] > 15:
                risk_factors.append("Very high mobility range")
                risk_score += 1
            
            # Low commute consistency
            if user_features['commute_consistency_score'] < 0.5:
                risk_factors.append("Irregular commute patterns")
                risk_score += 1
            
            if risk_score <= 1:
                risk_level = "LOW"
                risk_desc = "Stable mobility patterns suggest employment and residential stability"
            elif risk_score <= 3:
                risk_level = "MEDIUM" 
                risk_desc = "Some mobility irregularities but generally stable"
            else:
                risk_level = "HIGH"
                risk_desc = "Multiple mobility risk factors detected"
            
            print(f"\n👤 USER {user_id} Risk Assessment:")
            print(f"   📊 Risk Level: {risk_level}")
            print(f"   🎯 Risk Score: {risk_score}/5")
            print(f"   💡 Description: {risk_desc}")
            if risk_factors:
                print(f"   ⚠️  Risk Factors: {', '.join(risk_factors)}")
            else:
                print(f"   ✅ No significant risk factors identified")
        
        print("\n📋 Feature Statistics:")
        print("-" * 50)
        for col in mobility_cols:
            values = enhanced_data[col]
            print(f"{col:.<40} {values.mean():.3f} ± {values.std():.3f}")
        
    except Exception as e:
        print(f"❌ Error creating mobility features: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ Mobility features test completed successfully!")
    print("\n💡 Integration Notes:")
    print("   - GPS data collection requires user consent and privacy considerations")
    print("   - Features can be integrated with traditional credit scoring models")
    print("   - Mobility patterns provide insights into employment and residential stability")
    print("   - Consider regulatory compliance for location data usage in credit decisions")

if __name__ == "__main__":
    main()
