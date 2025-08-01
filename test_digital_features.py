"""
Test script to demonstrate digital footprint feature engineering.

This script shows how to use the new create_digital_footprint_features method
to engineer features from digital transaction data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.data_processing.feature_engineering import FeatureEngineer

# Create sample main dataframe (simulating credit application data)
np.random.seed(42)
n_customers = 100

main_df = pd.DataFrame({
    'SK_ID_CURR': range(1, n_customers + 1),
    'AMT_INCOME_TOTAL': np.random.normal(200000, 50000, n_customers),
    'AMT_CREDIT': np.random.normal(500000, 100000, n_customers),
    'TARGET': np.random.binomial(1, 0.1, n_customers)  # 10% default rate
})

# Create sample digital transaction data
n_transactions = 5000
transaction_dates = pd.date_range(
    start='2023-01-01', 
    end='2023-12-31', 
    periods=n_transactions
)

# Define transaction categories
essential_categories = [
    'utilities', 'groceries', 'healthcare', 'insurance', 
    'transportation', 'education', 'rent'
]
discretionary_categories = [
    'entertainment', 'dining', 'shopping', 'travel', 
    'gaming', 'electronics', 'clothing'
]
all_categories = essential_categories + discretionary_categories

digital_data = pd.DataFrame({
    'user_id': np.random.randint(1, n_customers + 1, n_transactions),
    'transaction_date': np.random.choice(transaction_dates, n_transactions),
    'amount': np.random.exponential(1000, n_transactions),  # Exponential distribution for amounts
    'category': np.random.choice(all_categories, n_transactions)
})

# Remove some users to simulate customers without digital transaction data
digital_data = digital_data[digital_data['user_id'] <= 80]  # Only 80% have digital data

print("Sample Data Created:")
print(f"Main DataFrame shape: {main_df.shape}")
print(f"Digital Data shape: {digital_data.shape}")
print(f"Unique users in digital data: {digital_data['user_id'].nunique()}")

print("\nDigital Data Sample:")
print(digital_data.head())

print("\nCategory Distribution:")
print(digital_data['category'].value_counts())

# Initialize FeatureEngineer
feature_engineer = FeatureEngineer()

# Create digital footprint features
print("\nCreating digital footprint features...")
try:
    enhanced_df = feature_engineer.create_digital_footprint_features(
        df=main_df,
        digital_data=digital_data,
        user_id_col='user_id',
        amount_col='amount',
        category_col='category',
        date_col='transaction_date'
    )
    
    print(f"Enhanced DataFrame shape: {enhanced_df.shape}")
    
    # Get the new feature names
    feature_names = feature_engineer.get_feature_names()
    digital_features = feature_names['digital_footprint']
    
    print(f"\nDigital Footprint Features Created ({len(digital_features)}):")
    for feature in digital_features:
        if feature in enhanced_df.columns:
            print(f"  ✓ {feature}")
        else:
            print(f"  ✗ {feature} (not found)")
    
    # Display sample statistics for key features
    print("\nKey Feature Statistics:")
    key_features = [
        'avg_monthly_transactions', 'avg_transaction_value', 
        'essential_discretionary_ratio', 'essential_spending_pct'
    ]
    
    for feature in key_features:
        if feature in enhanced_df.columns:
            print(f"\n{feature}:")
            print(f"  Mean: {enhanced_df[feature].mean():.2f}")
            print(f"  Std:  {enhanced_df[feature].std():.2f}")
            print(f"  Min:  {enhanced_df[feature].min():.2f}")
            print(f"  Max:  {enhanced_df[feature].max():.2f}")
            print(f"  Non-zero values: {(enhanced_df[feature] > 0).sum()}/{len(enhanced_df)}")
    
    # Show correlation with target variable
    print("\nCorrelation with TARGET variable:")
    correlations = []
    for feature in key_features:
        if feature in enhanced_df.columns:
            corr = enhanced_df[feature].corr(enhanced_df['TARGET'])
            correlations.append((feature, corr))
            print(f"  {feature}: {corr:.4f}")
    
    # Save results
    output_file = "enhanced_data_with_digital_features.csv"
    enhanced_df.to_csv(output_file, index=False)
    print(f"\nEnhanced data saved to: {output_file}")
    
    print("\n" + "="*60)
    print("DIGITAL FOOTPRINT FEATURES SUCCESSFULLY CREATED!")
    print("="*60)
    
except Exception as e:
    print(f"Error creating digital footprint features: {e}")
    import traceback
    traceback.print_exc()
