"""
Test script to demonstrate utility/telecom feature engineering.

This script shows how to use the new create_utility_features method
to engineer features from utility and telecom payment/usage data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_processing.feature_engineering import FeatureEngineer

# Create sample main dataframe (simulating credit application data)
np.random.seed(42)
n_customers = 150

main_df = pd.DataFrame({
    'SK_ID_CURR': range(1, n_customers + 1),
    'AMT_INCOME_TOTAL': np.random.normal(200000, 50000, n_customers),
    'AMT_CREDIT': np.random.normal(500000, 100000, n_customers),
    'TARGET': np.random.binomial(1, 0.1, n_customers)  # 10% default rate
})

# Create sample utility/telecom data
def create_utility_payment_data():
    """Create realistic utility/telecom payment and usage data"""
    
    utility_data = []
    service_types = ['electricity', 'gas', 'water', 'telecom', 'internet']
    
    # Reference date for calculations
    end_date = datetime(2023, 12, 31)
    
    for customer_id in range(1, n_customers + 1):
        # Random registration date (1-60 months ago)
        months_ago = np.random.randint(1, 61)
        registration_date = end_date - timedelta(days=months_ago * 30)
        
        # Customer behavior profile
        is_stable_customer = np.random.choice([True, False], p=[0.75, 0.25])
        is_high_usage_customer = np.random.choice([True, False], p=[0.3, 0.7])
        
        # Number of services (stable customers tend to have more services)
        if is_stable_customer:
            num_services = np.random.choice([2, 3, 4], p=[0.3, 0.5, 0.2])
        else:
            num_services = np.random.choice([1, 2, 3], p=[0.5, 0.4, 0.1])
        
        customer_services = np.random.choice(service_types, num_services, replace=False)
        
        # Generate monthly payments for each service
        current_date = registration_date
        while current_date <= end_date:
            
            for service_type in customer_services:
                # Base amounts by service type
                base_amounts = {
                    'electricity': 120,
                    'gas': 80,
                    'water': 60,
                    'telecom': 50,
                    'internet': 45
                }
                
                base_usage = {
                    'electricity': 800,  # kWh
                    'gas': 50,          # therms
                    'water': 5000,      # gallons
                    'telecom': 2000,    # minutes
                    'internet': 500     # GB
                }
                
                base_payment = base_amounts[service_type]
                base_usage_amount = base_usage[service_type]
                
                # Add variability based on customer profile
                if is_stable_customer:
                    # Stable customers have less variation
                    payment_variation = np.random.normal(0, base_payment * 0.15)
                    usage_variation = np.random.normal(0, base_usage_amount * 0.15)
                else:
                    # Unstable customers have more variation
                    payment_variation = np.random.normal(0, base_payment * 0.35)
                    usage_variation = np.random.normal(0, base_usage_amount * 0.35)
                
                # High usage customers use more
                if is_high_usage_customer:
                    payment_variation += base_payment * 0.3
                    usage_variation += base_usage_amount * 0.3
                
                final_payment = max(10, base_payment + payment_variation)  # Minimum $10
                final_usage = max(1, base_usage_amount + usage_variation)   # Minimum 1 unit
                
                # Sometimes customers miss payments (unstable customers more likely)
                if is_stable_customer:
                    payment_probability = 0.98
                else:
                    payment_probability = 0.85
                
                if np.random.random() < payment_probability:
                    # Payment delay (stable customers pay on time more often)
                    if is_stable_customer:
                        payment_delay = np.random.choice([0, 1, 2], p=[0.9, 0.08, 0.02])
                    else:
                        payment_delay = np.random.choice([0, 1, 2, 3, 5], p=[0.6, 0.2, 0.1, 0.05, 0.05])
                    
                    payment_date = current_date + timedelta(days=payment_delay)
                    
                    utility_data.append({
                        'customer_id': customer_id,
                        'service_type': service_type,
                        'payment_date': payment_date,
                        'payment_amount': round(final_payment, 2),
                        'usage_amount': round(final_usage, 1),
                        'registration_date': registration_date,
                        'is_stable_profile': is_stable_customer
                    })
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
    
    return pd.DataFrame(utility_data)

# Generate utility data
print("Creating utility/telecom payment and usage data...")
utility_data = create_utility_payment_data()

print(f"Main DataFrame shape: {main_df.shape}")
print(f"Utility Data shape: {utility_data.shape}")
print(f"Unique customers in utility data: {utility_data['customer_id'].nunique()}")
print(f"Date range: {utility_data['payment_date'].min()} to {utility_data['payment_date'].max()}")

print("\nUtility Data Sample:")
print(utility_data.head(10))

print("\nService Type Distribution:")
print(utility_data['service_type'].value_counts())

print("\nCustomer Service Counts:")
service_counts = utility_data.groupby('customer_id')['service_type'].nunique()
print(service_counts.value_counts().sort_index())

# Initialize FeatureEngineer
feature_engineer = FeatureEngineer()

# Create utility features
print("\nCreating utility/telecom features...")
try:
    enhanced_df = feature_engineer.create_utility_features(
        df=main_df,
        utility_data=utility_data,
        user_id_col='customer_id',
        payment_amount_col='payment_amount',
        usage_amount_col='usage_amount',
        payment_date_col='payment_date',
        registration_date_col='registration_date',
        service_type_col='service_type'
    )
    
    print(f"Enhanced DataFrame shape: {enhanced_df.shape}")
    
    # Get the new feature names
    feature_names = feature_engineer.get_feature_names()
    utility_features = feature_names['utility_telecom']
    
    print(f"\nUtility/Telecom Features Created ({len(utility_features)}):")
    created_features = []
    for feature in utility_features:
        if feature in enhanced_df.columns:
            created_features.append(feature)
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} (not found)")
    
    print(f"\nSuccessfully created {len(created_features)} utility features")
    
    # Display sample statistics for key features
    print("\nKey Feature Statistics:")
    key_features = [
        'payment_stability_score', 'tenure_months', 'usage_volatility_3m', 
        'payment_regularity_score', 'utility_stability_score'
    ]
    
    for feature in key_features:
        if feature in enhanced_df.columns:
            print(f"\n{feature}:")
            print(f"  Mean: {enhanced_df[feature].mean():.2f}")
            print(f"  Std:  {enhanced_df[feature].std():.2f}")
            print(f"  Min:  {enhanced_df[feature].min():.2f}")
            print(f"  Max:  {enhanced_df[feature].max():.2f}")
            print(f"  Non-zero values: {(enhanced_df[feature] > 0).sum()}/{len(enhanced_df)}")
    
    # Analyze feature distributions
    print("\nFeature Analysis:")
    
    # Payment consistency analysis
    high_consistency = (enhanced_df['payment_consistency_cv'] < 0.2).sum()
    print(f"Customers with high payment consistency (CV < 0.2): {high_consistency} ({high_consistency/len(enhanced_df):.1%})")
    
    # Tenure analysis
    long_tenure = (enhanced_df['tenure_months'] > 24).sum()
    print(f"Customers with long tenure (>24 months): {long_tenure} ({long_tenure/len(enhanced_df):.1%})")
    
    # Usage volatility analysis
    if 'usage_volatility_3m' in enhanced_df.columns:
        low_volatility = (enhanced_df['usage_volatility_3m'] < enhanced_df['usage_volatility_3m'].median()).sum()
        print(f"Customers with low usage volatility: {low_volatility} ({low_volatility/len(enhanced_df):.1%})")
    
    # Overall stability analysis
    high_stability = (enhanced_df['utility_stability_score'] > 75).sum()
    print(f"Customers with high utility stability (>75): {high_stability} ({high_stability/len(enhanced_df):.1%})")
    
    # Correlation with target variable
    print("\nCorrelation with TARGET variable:")
    target_correlations = []
    for feature in key_features:
        if feature in enhanced_df.columns:
            corr = enhanced_df[feature].corr(enhanced_df['TARGET'])
            target_correlations.append((feature, corr))
            print(f"  {feature}: {corr:.4f}")
    
    # Show sample of enhanced data
    print("\nSample Enhanced Data:")
    sample_cols = ['SK_ID_CURR', 'TARGET'] + key_features[:3]
    print(enhanced_df[sample_cols].head(10))
    
    # Save results
    output_file = "enhanced_data_with_utility_features.csv"
    enhanced_df.to_csv(output_file, index=False)
    print(f"\nEnhanced data saved to: {output_file}")
    
    print("\n" + "="*70)
    print("UTILITY/TELECOM FEATURES SUCCESSFULLY CREATED!")
    print("="*70)
    
    print(f"""
FEATURE SUMMARY:
• Payment Consistency: Measures stability of monthly bill payments
• Customer Tenure: Length of relationship with utility/telecom providers
• Usage Volatility: 3-month rolling standard deviation of usage patterns
• Payment Regularity: Consistency of payment timing
• Overall Stability Score: Composite score combining all factors

CREDIT RISK INSIGHTS:
• Stable payment patterns indicate financial discipline
• Long tenure suggests residential and income stability
• Low usage volatility indicates predictable lifestyle
• Regular payments predict loan payment behavior
• Multiple services suggest financial capacity
""")
    
except Exception as e:
    print(f"Error creating utility features: {e}")
    import traceback
    traceback.print_exc()
