"""
Feature engineering utilities for credit risk model.

This module provides utilities for creating new features from existing ones,
including polynomial features, domain-specific financial ratios, and 
digital footprint features from alternative data sources.
"""

import pandas as pd
import numpy as np
from itertools import combinations
from typing import List, Optional, Dict

# Note: geopy and sklearn are imported within methods to avoid dependency issues
# Make sure to install: pip install geopy scikit-learn


class FeatureEngineer:
    """A class for creating new features from existing ones.

    This class provides methods for generating polynomial features,
    domain-specific financial ratios, and digital footprint features
    for credit risk assessment from both traditional and alternative data sources.
    """

    def __init__(self):
        """Initialize the FeatureEngineer."""
        self.feature_names = {}
        self.ext_source_cols = ['EXT_SOURCE_1', 'EXT_SOURCE_2', 'EXT_SOURCE_3']

    def create_polynomial_features(
        self, 
        df: pd.DataFrame, 
        degree: int = 2,
        include_original: bool = True
    ) -> pd.DataFrame:
        """
        Create polynomial interaction features for external source scores.

        Args:
            df: Input DataFrame
            degree: Degree of polynomial features (default: 2)
            include_original: Whether to include original features (default: True)

        Returns:
            DataFrame with added polynomial features
        """
        df = df.copy()
        
        # Validate external source columns exist
        missing_cols = [col for col in self.ext_source_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Get combinations of features for interactions
        for r in range(2, degree + 1):
            for cols in combinations(self.ext_source_cols, r):
                # Create feature name
                feature_name = f"{'_'.join(cols)}_interaction"
                
                # Calculate interaction term
                df[feature_name] = df[list(cols)].prod(axis=1)
        
        # Drop original features if not needed
        if not include_original:
            df = df.drop(columns=self.ext_source_cols)
        
        return df

    def create_credit_ratios(
        self, 
        df: pd.DataFrame,
        income_col: str = 'AMT_INCOME_TOTAL',
        credit_col: str = 'AMT_CREDIT',
        annuity_col: str = 'AMT_ANNUITY',
        days_employed_col: str = 'DAYS_EMPLOYED',
        days_birth_col: str = 'DAYS_BIRTH'
    ) -> pd.DataFrame:
        """
        Create domain-specific financial ratios.

        Args:
            df: Input DataFrame
            income_col: Name of income column
            credit_col: Name of credit amount column
            annuity_col: Name of annuity column
            days_employed_col: Name of employment duration column
            days_birth_col: Name of birth days column

        Returns:
            DataFrame with added ratio features
        """
        df = df.copy()
        
        # Validate required columns exist
        required_cols = [
            income_col, credit_col, annuity_col, 
            days_employed_col, days_birth_col
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns: {missing_cols}")
        
        # Create CREDIT_INCOME_PERCENT
        df['CREDIT_INCOME_PERCENT'] = df[credit_col] / df[income_col] * 100
        
        # Create ANNUITY_INCOME_PERCENT
        df['ANNUITY_INCOME_PERCENT'] = df[annuity_col] / df[income_col] * 100
        
        # Create CREDIT_TERM (credit amount divided by annuity)
        df['CREDIT_TERM'] = df[credit_col] / df[annuity_col]
        
        # Create DAYS_EMPLOYED_PERCENT
        # Note: Convert days to positive values for calculation
        df['DAYS_EMPLOYED_PERCENT'] = (
            (df[days_employed_col] * -1) / (df[days_birth_col] * -1) * 100
        )
        
        return df

    def create_payment_ratios(
        self, 
        df: pd.DataFrame,
        previous_loans: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Create payment behavior ratios from previous loans if available.

        Args:
            df: Input DataFrame
            previous_loans: Optional DataFrame containing previous loan information

        Returns:
            DataFrame with added payment ratio features
        """
        df = df.copy()
        
        if previous_loans is not None:
            # Calculate average payment ratios from previous loans
            payment_ratios = previous_loans.groupby('SK_ID_CURR').agg({
                'AMT_PAYMENT': 'mean',
                'AMT_INSTALMENT': 'mean'
            })
            
            payment_ratios['PAYMENT_RATIO'] = (
                payment_ratios['AMT_PAYMENT'] / payment_ratios['AMT_INSTALMENT']
            )
            
            # Merge with main DataFrame
            df = df.merge(
                payment_ratios[['PAYMENT_RATIO']], 
                left_on='SK_ID_CURR',
                right_index=True,
                how='left'
            )
        
        return df

    def create_digital_footprint_features(
        self,
        df: pd.DataFrame,
        digital_data: pd.DataFrame,
        user_id_col: str = 'user_id',
        amount_col: str = 'amount',
        category_col: str = 'category',
        date_col: str = 'transaction_date'
    ) -> pd.DataFrame:
        """
        Create digital footprint features from digital transaction data.

        This method engineers features from digital transaction data like UPI,
        e-commerce, and digital payment transactions to assess spending behavior
        and financial patterns.

        Args:
            df: Main DataFrame to add features to
            digital_data: DataFrame containing digital transaction data
            user_id_col: Column name for user identifier
            amount_col: Column name for transaction amount
            category_col: Column name for transaction category
            date_col: Column name for transaction date

        Returns:
            DataFrame with added digital footprint features
        """
        df = df.copy()
        
        # Validate required columns exist in digital_data
        required_cols = [user_id_col, amount_col, category_col, date_col]
        missing_cols = [col for col in required_cols if col not in digital_data.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in digital_data: {missing_cols}")
        
        # Ensure date column is datetime
        digital_data = digital_data.copy()
        digital_data[date_col] = pd.to_datetime(digital_data[date_col])
        
        # Define essential vs discretionary spending categories
        essential_categories = {
            'utilities', 'electricity', 'water', 'gas', 'internet', 'telecom',
            'groceries', 'food', 'medicine', 'healthcare', 'insurance',
            'rent', 'mortgage', 'loan_payment', 'education', 'transportation'
        }
        
        discretionary_categories = {
            'entertainment', 'dining', 'shopping', 'travel', 'gaming',
            'streaming', 'music', 'sports', 'luxury', 'electronics',
            'clothing', 'books', 'hobbies', 'gifts'
        }
        
        # Create spending category indicators
        digital_data['is_essential'] = digital_data[category_col].str.lower().apply(
            lambda x: 1 if any(cat in str(x).lower() for cat in essential_categories) else 0
        )
        digital_data['is_discretionary'] = digital_data[category_col].str.lower().apply(
            lambda x: 1 if any(cat in str(x).lower() for cat in discretionary_categories) else 0
        )
        
        # Extract month-year for monthly aggregations
        digital_data['month_year'] = digital_data[date_col].dt.to_period('M')
        
        # 1. Transaction Frequency Features
        monthly_freq = digital_data.groupby([user_id_col, 'month_year']).size().reset_index(name='monthly_transactions')
        avg_monthly_freq = monthly_freq.groupby(user_id_col)['monthly_transactions'].agg([
            ('avg_monthly_transactions', 'mean'),
            ('std_monthly_transactions', 'std'),
            ('max_monthly_transactions', 'max'),
            ('min_monthly_transactions', 'min')
        ]).reset_index()
        
        # Overall transaction frequency
        total_freq = digital_data.groupby(user_id_col).size().reset_index(name='total_transactions')
        
        # Days between transactions
        transaction_gaps = digital_data.groupby(user_id_col)[date_col].apply(
            lambda x: x.sort_values().diff().dt.days.mean() if len(x) > 1 else 0
        ).reset_index(name='avg_days_between_transactions')
        
        # 2. Average Transaction Value Features
        transaction_values = digital_data.groupby(user_id_col)[amount_col].agg([
            ('avg_transaction_value', 'mean'),
            ('median_transaction_value', 'median'),
            ('std_transaction_value', 'std'),
            ('max_transaction_value', 'max'),
            ('min_transaction_value', 'min'),
            ('total_transaction_value', 'sum')
        ]).reset_index()
        
        # Monthly spending patterns
        monthly_spending = digital_data.groupby([user_id_col, 'month_year'])[amount_col].sum().reset_index()
        avg_monthly_spending = monthly_spending.groupby(user_id_col)[amount_col].agg([
            ('avg_monthly_spending', 'mean'),
            ('std_monthly_spending', 'std')
        ]).reset_index()
        
        # 3. Spending Patterns Features
        essential_spending = digital_data[digital_data['is_essential'] == 1].groupby(user_id_col)[amount_col].agg([
            ('essential_spending_total', 'sum'),
            ('essential_spending_avg', 'mean'),
            ('essential_transaction_count', 'count')
        ]).reset_index()
        
        discretionary_spending = digital_data[digital_data['is_discretionary'] == 1].groupby(user_id_col)[amount_col].agg([
            ('discretionary_spending_total', 'sum'),
            ('discretionary_spending_avg', 'mean'),
            ('discretionary_transaction_count', 'count')
        ]).reset_index()
        
        # Calculate spending ratios
        spending_ratios = essential_spending.merge(
            discretionary_spending, on=user_id_col, how='outer'
        ).fillna(0)
        
        # Essential to discretionary spending ratio
        spending_ratios['essential_discretionary_ratio'] = np.where(
            spending_ratios['discretionary_spending_total'] > 0,
            spending_ratios['essential_spending_total'] / spending_ratios['discretionary_spending_total'],
            np.inf  # If no discretionary spending, ratio is infinite (very conservative)
        )
        
        # Essential spending percentage of total
        total_spending_by_user = digital_data.groupby(user_id_col)[amount_col].sum().reset_index(name='total_user_spending')
        spending_ratios = spending_ratios.merge(total_spending_by_user, on=user_id_col)
        
        spending_ratios['essential_spending_pct'] = (
            spending_ratios['essential_spending_total'] / spending_ratios['total_user_spending'] * 100
        )
        spending_ratios['discretionary_spending_pct'] = (
            spending_ratios['discretionary_spending_total'] / spending_ratios['total_user_spending'] * 100
        )
        
        # Additional behavioral features
        behavioral_features = digital_data.groupby(user_id_col).agg({
            category_col: lambda x: x.nunique(),  # Number of unique categories
            date_col: [
                lambda x: (x.max() - x.min()).days,  # Transaction span in days
                lambda x: x.dt.hour.std(),  # Time consistency (std of hours)
                lambda x: x.dt.dayofweek.std()  # Day of week consistency
            ]
        }).reset_index()
        
        # Flatten column names for behavioral features
        behavioral_features.columns = [
            user_id_col, 'unique_categories', 'transaction_span_days',
            'time_consistency', 'day_consistency'
        ]
        
        # Merge all features
        digital_features = total_freq
        for feature_df in [avg_monthly_freq, transaction_gaps, transaction_values, 
                          avg_monthly_spending, spending_ratios, behavioral_features]:
            digital_features = digital_features.merge(feature_df, on=user_id_col, how='left')
        
        # Handle infinite values and fill NaN
        digital_features = digital_features.replace([np.inf, -np.inf], np.nan)
        digital_features = digital_features.fillna(0)
        
        # Map user_id to the main dataframe identifier (assuming SK_ID_CURR)
        # This assumes there's a mapping between user_id and SK_ID_CURR
        if 'SK_ID_CURR' in df.columns and user_id_col in digital_features.columns:
            # If direct mapping exists, merge directly
            df = df.merge(
                digital_features.drop(columns=[user_id_col]), 
                left_on='SK_ID_CURR',
                right_on=user_id_col if user_id_col in digital_features.columns else 'SK_ID_CURR',
                how='left'
            )
        else:
            # If no direct mapping, assume user_id corresponds to SK_ID_CURR
            digital_features = digital_features.rename(columns={user_id_col: 'SK_ID_CURR'})
            df = df.merge(digital_features, on='SK_ID_CURR', how='left')
        
        # Fill NaN values for users without digital transaction data
        digital_feature_cols = [col for col in digital_features.columns if col != 'SK_ID_CURR']
        df[digital_feature_cols] = df[digital_feature_cols].fillna(0)
        
        return df

    def create_utility_features(
        self,
        df: pd.DataFrame,
        utility_data: pd.DataFrame,
        user_id_col: str = 'customer_id',
        payment_amount_col: str = 'payment_amount',
        usage_amount_col: str = 'usage_amount',
        payment_date_col: str = 'payment_date',
        registration_date_col: str = 'registration_date',
        service_type_col: str = 'service_type'
    ) -> pd.DataFrame:
        """
        Create utility and telecom features from payment and usage data.

        This method engineers features from utility/telecom payment data including
        payment consistency, customer tenure, and usage volatility patterns that
        indicate financial stability and behavioral predictability.

        Args:
            df: Main DataFrame to add features to
            utility_data: DataFrame containing utility/telecom payment and usage data
            user_id_col: Column name for user identifier
            payment_amount_col: Column name for payment amount
            usage_amount_col: Column name for usage amount (data, calls, etc.)
            payment_date_col: Column name for payment date
            registration_date_col: Column name for service registration date
            service_type_col: Column name for service type (telecom, electricity, etc.)

        Returns:
            DataFrame with added utility/telecom features
        """
        df = df.copy()
        
        # Validate required columns exist in utility_data
        required_cols = [user_id_col, payment_amount_col, payment_date_col]
        missing_cols = [col for col in required_cols if col not in utility_data.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in utility_data: {missing_cols}")
        
        # Ensure date columns are datetime
        utility_data = utility_data.copy()
        utility_data[payment_date_col] = pd.to_datetime(utility_data[payment_date_col])
        
        if registration_date_col in utility_data.columns:
            utility_data[registration_date_col] = pd.to_datetime(utility_data[registration_date_col])
        
        # Extract month-year for monthly aggregations
        utility_data['payment_month'] = utility_data[payment_date_col].dt.to_period('M')
        
        # 1. PAYMENT CONSISTENCY FEATURES
        # Monthly payment amounts for consistency calculation
        monthly_payments = utility_data.groupby([user_id_col, 'payment_month'])[payment_amount_col].sum().reset_index()
        
        payment_consistency = monthly_payments.groupby(user_id_col)[payment_amount_col].agg([
            ('avg_monthly_payment', 'mean'),
            ('std_monthly_payment', 'std'),
            ('min_monthly_payment', 'min'),
            ('max_monthly_payment', 'max'),
            ('payment_months_count', 'count')
        ]).reset_index()
        
        # Calculate coefficient of variation for payment consistency
        payment_consistency['payment_consistency_cv'] = (
            payment_consistency['std_monthly_payment'] / payment_consistency['avg_monthly_payment']
        ).fillna(0)
        
        # Payment stability score (lower CV = higher stability)
        payment_consistency['payment_stability_score'] = np.where(
            payment_consistency['payment_consistency_cv'] == 0, 100,
            100 - (payment_consistency['payment_consistency_cv'] * 100)
        ).clip(0, 100)
        
        # Payment range (max - min) as another consistency measure
        payment_consistency['payment_range'] = (
            payment_consistency['max_monthly_payment'] - payment_consistency['min_monthly_payment']
        )
        
        # 2. TENURE FEATURES
        tenure_features = pd.DataFrame()
        
        if registration_date_col in utility_data.columns:
            # Calculate tenure from registration date
            reference_date = utility_data[payment_date_col].max()
            customer_registration = utility_data.groupby(user_id_col)[registration_date_col].first().reset_index()
            
            customer_registration['tenure_days'] = (
                reference_date - customer_registration[registration_date_col]
            ).dt.days
            
            customer_registration['tenure_months'] = customer_registration['tenure_days'] / 30.44  # Average days per month
            customer_registration['tenure_years'] = customer_registration['tenure_months'] / 12
            
            tenure_features = customer_registration[[user_id_col, 'tenure_days', 'tenure_months', 'tenure_years']]
        else:
            # Calculate tenure from payment history span
            payment_span = utility_data.groupby(user_id_col)[payment_date_col].agg([
                ('first_payment_date', 'min'),
                ('last_payment_date', 'max')
            ]).reset_index()
            
            payment_span['tenure_days'] = (
                payment_span['last_payment_date'] - payment_span['first_payment_date']
            ).dt.days + 1  # +1 to include both start and end dates
            
            payment_span['tenure_months'] = payment_span['tenure_days'] / 30.44
            payment_span['tenure_years'] = payment_span['tenure_months'] / 12
            
            tenure_features = payment_span[[user_id_col, 'tenure_days', 'tenure_months', 'tenure_years']]
        
        # Tenure stability categories
        def categorize_tenure(months):
            if months < 3:
                return 'New_Customer'
            elif months < 12:
                return 'Short_Term'
            elif months < 24:
                return 'Medium_Term'
            elif months < 48:
                return 'Long_Term'
            else:
                return 'Very_Stable'
        
        tenure_features['tenure_category'] = tenure_features['tenure_months'].apply(categorize_tenure)
        
        # 3. USAGE VOLATILITY FEATURES
        usage_volatility_features = pd.DataFrame()
        
        if usage_amount_col in utility_data.columns:
            # Monthly usage aggregation
            monthly_usage = utility_data.groupby([user_id_col, 'payment_month'])[usage_amount_col].sum().reset_index()
            monthly_usage = monthly_usage.sort_values([user_id_col, 'payment_month'])
            
            # Calculate rolling 3-month usage volatility
            usage_volatility_list = []
            
            for customer_id in monthly_usage[user_id_col].unique():
                customer_usage = monthly_usage[monthly_usage[user_id_col] == customer_id]
                
                if len(customer_usage) >= 3:
                    # Rolling 3-month standard deviation
                    customer_usage['rolling_3m_std'] = customer_usage[usage_amount_col].rolling(
                        window=3, min_periods=3
                    ).std()
                    
                    # Calculate overall usage statistics
                    usage_stats = {
                        user_id_col: customer_id,
                        'avg_usage': customer_usage[usage_amount_col].mean(),
                        'std_usage': customer_usage[usage_amount_col].std(),
                        'usage_cv': customer_usage[usage_amount_col].std() / customer_usage[usage_amount_col].mean() if customer_usage[usage_amount_col].mean() > 0 else 0,
                        'usage_volatility_3m': customer_usage['rolling_3m_std'].mean(),  # Average of rolling stds
                        'max_usage_volatility_3m': customer_usage['rolling_3m_std'].max(),
                        'min_usage': customer_usage[usage_amount_col].min(),
                        'max_usage': customer_usage[usage_amount_col].max(),
                        'usage_range': customer_usage[usage_amount_col].max() - customer_usage[usage_amount_col].min(),
                        'usage_trend_slope': 0  # Will be calculated below
                    }
                    
                    # Calculate usage trend
                    if len(customer_usage) > 1:
                        months_numeric = np.arange(len(customer_usage))
                        slope, _ = np.polyfit(months_numeric, customer_usage[usage_amount_col].values, 1)
                        usage_stats['usage_trend_slope'] = slope
                    
                    usage_volatility_list.append(usage_stats)
                else:
                    # Not enough data for rolling calculation
                    usage_stats = {
                        user_id_col: customer_id,
                        'avg_usage': customer_usage[usage_amount_col].mean(),
                        'std_usage': customer_usage[usage_amount_col].std() if len(customer_usage) > 1 else 0,
                        'usage_cv': 0,
                        'usage_volatility_3m': 0,
                        'max_usage_volatility_3m': 0,
                        'min_usage': customer_usage[usage_amount_col].min(),
                        'max_usage': customer_usage[usage_amount_col].max(),
                        'usage_range': customer_usage[usage_amount_col].max() - customer_usage[usage_amount_col].min() if len(customer_usage) > 1 else 0,
                        'usage_trend_slope': 0
                    }
                    usage_volatility_list.append(usage_stats)
            
            usage_volatility_features = pd.DataFrame(usage_volatility_list)
            
            # Usage consistency score (lower volatility = higher score)
            if len(usage_volatility_features) > 0:
                max_volatility = usage_volatility_features['usage_volatility_3m'].max()
                usage_volatility_features['usage_consistency_score'] = np.where(
                    max_volatility == 0, 100,
                    100 - (usage_volatility_features['usage_volatility_3m'] / max_volatility * 100)
                ).clip(0, 100)
        
        # 4. SERVICE TYPE FEATURES (if available)
        service_features = pd.DataFrame()
        if service_type_col in utility_data.columns:
            # Count of different service types per customer
            service_counts = utility_data.groupby(user_id_col)[service_type_col].agg([
                ('unique_services_count', 'nunique'),
                ('primary_service_type', lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown')
            ]).reset_index()
            
            # Service engagement score
            service_counts['service_engagement_score'] = service_counts['unique_services_count'] * 20  # Each service worth 20 points
            service_counts['service_engagement_score'] = service_counts['service_engagement_score'].clip(0, 100)
            
            service_features = service_counts
        
        # 5. PAYMENT BEHAVIOR PATTERNS
        payment_behavior = utility_data.groupby(user_id_col).agg({
            payment_date_col: [
                ('payment_frequency', 'count'),
                ('first_payment', 'min'),
                ('last_payment', 'max')
            ]
        }).reset_index()
        
        # Flatten column names
        payment_behavior.columns = [user_id_col, 'total_payments', 'first_payment_date', 'last_payment_date']
        
        # Calculate payment regularity
        payment_behavior['payment_span_days'] = (
            payment_behavior['last_payment_date'] - payment_behavior['first_payment_date']
        ).dt.days + 1
        
        payment_behavior['avg_days_between_payments'] = np.where(
            payment_behavior['total_payments'] > 1,
            payment_behavior['payment_span_days'] / (payment_behavior['total_payments'] - 1),
            0
        )
        
        # Payment regularity score (consistent intervals = higher score)
        expected_monthly_payments = payment_behavior['payment_span_days'] / 30.44
        actual_payments = payment_behavior['total_payments']
        payment_behavior['payment_regularity_score'] = np.where(
            expected_monthly_payments > 0,
            (actual_payments / expected_monthly_payments * 100).clip(0, 100),
            0
        )
        
        # Merge all utility features
        utility_features = payment_consistency
        
        feature_dfs = [tenure_features, payment_behavior]
        if len(usage_volatility_features) > 0:
            feature_dfs.append(usage_volatility_features)
        if len(service_features) > 0:
            feature_dfs.append(service_features)
        
        for feature_df in feature_dfs:
            if len(feature_df) > 0:
                utility_features = utility_features.merge(feature_df, on=user_id_col, how='left')
        
        # Fill NaN values
        numeric_cols = utility_features.select_dtypes(include=[np.number]).columns
        utility_features[numeric_cols] = utility_features[numeric_cols].fillna(0)
        
        # Create overall utility stability score
        utility_features['utility_stability_score'] = (
            utility_features['payment_stability_score'] * 0.4 +  # 40% payment consistency
            (utility_features['tenure_months'].clip(0, 24) / 24 * 100) * 0.3 +  # 30% tenure (capped at 2 years)
            utility_features.get('usage_consistency_score', 0) * 0.2 +  # 20% usage consistency
            utility_features['payment_regularity_score'] * 0.1  # 10% payment regularity
        ).round(1)
        
        # Map user_id to the main dataframe identifier
        if 'SK_ID_CURR' in df.columns and user_id_col in utility_features.columns:
            if user_id_col != 'SK_ID_CURR':
                utility_features = utility_features.rename(columns={user_id_col: 'SK_ID_CURR'})
            df = df.merge(utility_features, on='SK_ID_CURR', how='left')
        else:
            # If no direct mapping, assume user_id corresponds to SK_ID_CURR
            utility_features = utility_features.rename(columns={user_id_col: 'SK_ID_CURR'})
            df = df.merge(utility_features, on='SK_ID_CURR', how='left')
        
        # Fill NaN values for users without utility data
        utility_feature_cols = [col for col in utility_features.columns if col != 'SK_ID_CURR']
        df[utility_feature_cols] = df[utility_feature_cols].fillna(0)
        
        return df

    def create_mobility_features(
        self,
        df: pd.DataFrame,
        gps_data: pd.DataFrame,
        user_id_col: str = 'SK_ID_CURR',
        timestamp_col: str = 'timestamp',
        latitude_col: str = 'latitude',
        longitude_col: str = 'longitude',
        tower_id_col: Optional[str] = 'tower_id',
        network_id_col: Optional[str] = 'network_id'
    ) -> pd.DataFrame:
        """
        Create mobility features from GPS trajectory data.
        
        Args:
            df: Main DataFrame to add features to
            gps_data: DataFrame with GPS trajectory data
            user_id_col: Column name for user ID (default: 'SK_ID_CURR')
            timestamp_col: Column name for timestamp (default: 'timestamp')
            latitude_col: Column name for latitude (default: 'latitude')
            longitude_col: Column name for longitude (default: 'longitude')
            tower_id_col: Column name for cellular tower ID (optional)
            network_id_col: Column name for WiFi network ID (optional)
            
        Returns:
            DataFrame with mobility features added
        """
        from geopy.distance import geodesic
        from sklearn.cluster import DBSCAN
        from datetime import datetime, time
        
        df = df.copy()
        
        # Validate required columns
        required_cols = [user_id_col, timestamp_col, latitude_col, longitude_col]
        missing_cols = [col for col in required_cols if col not in gps_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in GPS data: {missing_cols}")
        
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(gps_data[timestamp_col]):
            gps_data = gps_data.copy()
            gps_data[timestamp_col] = pd.to_datetime(gps_data[timestamp_col])
        
        # Add time-based features
        gps_data = gps_data.copy()
        gps_data['hour'] = gps_data[timestamp_col].dt.hour
        gps_data['weekday'] = gps_data[timestamp_col].dt.weekday
        gps_data['date'] = gps_data[timestamp_col].dt.date
        
        mobility_features_list = []
        
        for user_id in df[user_id_col].unique():
            user_gps = gps_data[gps_data[user_id_col] == user_id].copy()
            
            if len(user_gps) == 0:
                # If no GPS data for user, fill with default values
                mobility_features_list.append(self._create_default_mobility_features(user_id))
                continue
            
            # Initialize feature dictionary
            features = {user_id_col: user_id}
            
            # 1. Location Stability Features
            features.update(self._calculate_location_stability(
                user_gps, tower_id_col, network_id_col
            ))
            
            # 2. Work-Home Consistency Features
            features.update(self._calculate_work_home_consistency(
                user_gps, latitude_col, longitude_col
            ))
            
            # 3. Travel Radius Features
            features.update(self._calculate_travel_radius(
                user_gps, latitude_col, longitude_col
            ))
            
            mobility_features_list.append(features)
        
        # Convert to DataFrame
        mobility_df = pd.DataFrame(mobility_features_list)
        
        # Merge with main DataFrame
        df = df.merge(mobility_df, on=user_id_col, how='left')
        
        # Fill any remaining NaN values with 0
        mobility_feature_cols = [col for col in mobility_df.columns if col != user_id_col]
        df[mobility_feature_cols] = df[mobility_feature_cols].fillna(0)
        
        return df
    
    def _create_default_mobility_features(self, user_id):
        """Create default mobility features for users with no GPS data."""
        return {
            'SK_ID_CURR': user_id,
            # Location Stability
            'unique_towers_count': 0,
            'unique_networks_count': 0,
            'primary_tower_frequency': 0,
            'primary_network_frequency': 0,
            'location_stability_score': 0,
            'tower_consistency_ratio': 0,
            'network_consistency_ratio': 0,
            # Work-Home Consistency
            'home_location_lat': 0,
            'home_location_lon': 0,
            'work_location_lat': 0,
            'work_location_lon': 0,
            'home_work_distance_km': 0,
            'commute_consistency_score': 0,
            'location_transition_count': 0,
            'work_home_travel_frequency': 0,
            'location_pattern_regularity': 0,
            # Travel Radius
            'centroid_lat': 0,
            'centroid_lon': 0,
            'radius_of_gyration_km': 0,
            'max_distance_from_centroid_km': 0,
            'avg_distance_from_centroid_km': 0,
            'mobility_range_95th_percentile': 0,
            'geographic_spread': 0,
            'movement_entropy': 0,
            'travel_radius_stability': 0
        }
    
    def _calculate_location_stability(self, user_gps, tower_id_col, network_id_col):
        """Calculate location stability features based on cellular towers and WiFi networks."""
        features = {}
        
        # Tower-based features
        if tower_id_col and tower_id_col in user_gps.columns:
            tower_counts = user_gps[tower_id_col].value_counts()
            features['unique_towers_count'] = len(tower_counts)
            features['primary_tower_frequency'] = tower_counts.iloc[0] / len(user_gps) if len(tower_counts) > 0 else 0
            features['tower_consistency_ratio'] = tower_counts.iloc[0] / tower_counts.sum() if len(tower_counts) > 0 else 0
        else:
            features['unique_towers_count'] = 0
            features['primary_tower_frequency'] = 0
            features['tower_consistency_ratio'] = 0
        
        # Network-based features
        if network_id_col and network_id_col in user_gps.columns:
            network_counts = user_gps[network_id_col].value_counts()
            features['unique_networks_count'] = len(network_counts)
            features['primary_network_frequency'] = network_counts.iloc[0] / len(user_gps) if len(network_counts) > 0 else 0
            features['network_consistency_ratio'] = network_counts.iloc[0] / network_counts.sum() if len(network_counts) > 0 else 0
        else:
            features['unique_networks_count'] = 0
            features['primary_network_frequency'] = 0
            features['network_consistency_ratio'] = 0
        
        # Overall location stability score
        tower_stability = features['tower_consistency_ratio'] if tower_id_col else 0
        network_stability = features['network_consistency_ratio'] if network_id_col else 0
        features['location_stability_score'] = (tower_stability + network_stability) / 2
        
        return features
    
    def _calculate_work_home_consistency(self, user_gps, latitude_col, longitude_col):
        """Calculate work-home consistency features using clustering."""
        from geopy.distance import geodesic
        from sklearn.cluster import DBSCAN
        
        features = {}
        
        # Separate work hours (9am-5pm) and night hours (10pm-6am)
        work_hours = user_gps[(user_gps['hour'] >= 9) & (user_gps['hour'] <= 17)]
        night_hours = user_gps[(user_gps['hour'] >= 22) | (user_gps['hour'] <= 6)]
        
        # Find work location using clustering
        work_location = self._find_primary_location(work_hours, latitude_col, longitude_col)
        features['work_location_lat'] = work_location[0] if work_location else 0
        features['work_location_lon'] = work_location[1] if work_location else 0
        
        # Find home location using clustering
        home_location = self._find_primary_location(night_hours, latitude_col, longitude_col)
        features['home_location_lat'] = home_location[0] if home_location else 0
        features['home_location_lon'] = home_location[1] if home_location else 0
        
        # Calculate distance between work and home
        if work_location and home_location:
            features['home_work_distance_km'] = geodesic(home_location, work_location).kilometers
        else:
            features['home_work_distance_km'] = 0
        
        # Calculate commute consistency
        if work_location and home_location:
            # Count transitions between work and home areas
            work_visits = len(work_hours)
            home_visits = len(night_hours)
            total_visits = len(user_gps)
            
            features['work_home_travel_frequency'] = (work_visits + home_visits) / total_visits if total_visits > 0 else 0
            features['commute_consistency_score'] = min(work_visits, home_visits) / max(work_visits, home_visits) if max(work_visits, home_visits) > 0 else 0
            
            # Count location transitions
            daily_patterns = user_gps.groupby('date').agg({
                latitude_col: ['min', 'max'],
                longitude_col: ['min', 'max']
            })
            features['location_transition_count'] = len(daily_patterns)
            
            # Pattern regularity
            features['location_pattern_regularity'] = 1 - (daily_patterns.std().mean() / daily_patterns.mean().mean()) if daily_patterns.mean().mean() != 0 else 0
        else:
            features['work_home_travel_frequency'] = 0
            features['commute_consistency_score'] = 0
            features['location_transition_count'] = 0
            features['location_pattern_regularity'] = 0
        
        return features
    
    def _calculate_travel_radius(self, user_gps, latitude_col, longitude_col):
        """Calculate travel radius and mobility range features."""
        from geopy.distance import geodesic
        
        features = {}
        
        # Calculate centroid of all locations
        centroid_lat = user_gps[latitude_col].mean()
        centroid_lon = user_gps[longitude_col].mean()
        features['centroid_lat'] = centroid_lat
        features['centroid_lon'] = centroid_lon
        
        # Calculate distances from centroid
        distances = user_gps.apply(
            lambda row: geodesic(
                (centroid_lat, centroid_lon),
                (row[latitude_col], row[longitude_col])
            ).kilometers,
            axis=1
        )
        
        # Radius of gyration (RMS distance from centroid)
        features['radius_of_gyration_km'] = np.sqrt((distances ** 2).mean())
        features['max_distance_from_centroid_km'] = distances.max()
        features['avg_distance_from_centroid_km'] = distances.mean()
        features['mobility_range_95th_percentile'] = distances.quantile(0.95)
        
        # Geographic spread
        lat_range = user_gps[latitude_col].max() - user_gps[latitude_col].min()
        lon_range = user_gps[longitude_col].max() - user_gps[longitude_col].min()
        features['geographic_spread'] = lat_range + lon_range
        
        # Movement entropy (Shannon entropy of location visits)
        location_counts = user_gps.groupby([latitude_col, longitude_col]).size()
        location_probs = location_counts / location_counts.sum()
        features['movement_entropy'] = -np.sum(location_probs * np.log2(location_probs + 1e-10))
        
        # Travel radius stability (coefficient of variation of daily travel ranges)
        daily_ranges = user_gps.groupby('date').apply(
            lambda group: geodesic(
                (group[latitude_col].min(), group[longitude_col].min()),
                (group[latitude_col].max(), group[longitude_col].max())
            ).kilometers
        )
        features['travel_radius_stability'] = daily_ranges.std() / daily_ranges.mean() if daily_ranges.mean() > 0 else 0
        
        return features
    
    def _find_primary_location(self, location_data, latitude_col, longitude_col):
        """Find the primary location using DBSCAN clustering."""
        from sklearn.cluster import DBSCAN
        
        if len(location_data) < 5:
            return None
        
        coords = location_data[[latitude_col, longitude_col]].values
        
        # DBSCAN clustering (eps ~ 100 meters in degrees)
        eps_degrees = 0.001  # Approximately 100 meters
        dbscan = DBSCAN(eps=eps_degrees, min_samples=3)
        clusters = dbscan.fit_predict(coords)
        
        # Find the largest cluster
        if len(set(clusters)) > 1:
            cluster_counts = pd.Series(clusters).value_counts()
            largest_cluster = cluster_counts.index[0]
            
            if largest_cluster != -1:  # Not noise
                cluster_coords = coords[clusters == largest_cluster]
                return [cluster_coords[:, 0].mean(), cluster_coords[:, 1].mean()]
        
        # If no clear cluster, return centroid of all points
        return [coords[:, 0].mean(), coords[:, 1].mean()]

    def create_device_features(
        self,
        df: pd.DataFrame,
        device_data: pd.DataFrame,
        user_id_col: str = 'SK_ID_CURR',
        device_model_col: str = 'device_model',
        app_list_col: Optional[str] = 'installed_apps',
        daily_data_col: Optional[str] = 'daily_data_usage_mb',
        wifi_data_col: Optional[str] = 'wifi_data_mb',
        cellular_data_col: Optional[str] = 'cellular_data_mb'
    ) -> pd.DataFrame:
        """
        Create device-based features for credit risk assessment.
        
        Args:
            df: Main DataFrame to add features to
            device_data: DataFrame with device and app usage data
            user_id_col: Column name for user ID (default: 'SK_ID_CURR')
            device_model_col: Column name for device model (default: 'device_model')
            app_list_col: Column name for installed apps list (optional)
            daily_data_col: Column name for daily data consumption (optional)
            wifi_data_col: Column name for WiFi data usage (optional)
            cellular_data_col: Column name for cellular data usage (optional)
            
        Returns:
            DataFrame with device features added
        """
        df = df.copy()
        
        # Validate required columns
        required_cols = [user_id_col, device_model_col]
        missing_cols = [col for col in required_cols if col not in device_data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in device data: {missing_cols}")
        
        device_features_list = []
        
        for user_id in df[user_id_col].unique():
            user_device = device_data[device_data[user_id_col] == user_id]
            
            if len(user_device) == 0:
                # If no device data for user, fill with default values
                device_features_list.append(self._create_default_device_features(user_id))
                continue
            
            # Take the first/most recent device record if multiple exist
            user_device = user_device.iloc[0]
            
            # Initialize feature dictionary
            features = {user_id_col: user_id}
            
            # 1. Device Age Proxy Features
            features.update(self._calculate_device_age_proxy(user_device, device_model_col))
            
            # 2. App Ecosystem Features
            features.update(self._calculate_app_ecosystem(user_device, app_list_col))
            
            # 3. Network Behavior Features
            features.update(self._calculate_network_behavior(
                user_device, daily_data_col, wifi_data_col, cellular_data_col
            ))
            
            device_features_list.append(features)
        
        # Convert to DataFrame
        device_df = pd.DataFrame(device_features_list)
        
        # Merge with main DataFrame
        df = df.merge(device_df, on=user_id_col, how='left')
        
        # Fill any remaining NaN values with 0
        device_feature_cols = [col for col in device_df.columns if col != user_id_col]
        df[device_feature_cols] = df[device_feature_cols].fillna(0)
        
        return df
    
    def _create_default_device_features(self, user_id):
        """Create default device features for users with no device data."""
        return {
            'SK_ID_CURR': user_id,
            # Device Age Proxy
            'device_age_months': 0,
            'device_generation_score': 0,
            'is_premium_device': 0,
            'device_value_tier': 0,
            'os_age_months': 0,
            # App Ecosystem
            'financial_apps_count': 0,
            'security_apps_count': 0,
            'productivity_apps_count': 0,
            'total_app_categories': 0,
            'financial_app_ratio': 0,
            'security_app_ratio': 0,
            'app_sophistication_score': 0,
            # Network Behavior
            'avg_daily_data_mb': 0,
            'wifi_cellular_ratio': 0,
            'data_usage_tier': 0,
            'network_efficiency_score': 0,
            'data_consumption_stability': 0,
            'preferred_network_type': 0
        }
    
    def _calculate_device_age_proxy(self, user_device, device_model_col):
        """Calculate device age proxy features based on device model."""
        from datetime import datetime
        
        # Device model release date lookup table
        device_release_dates = {
            # iPhone models
            'iPhone 14 Pro Max': '2022-09-16',
            'iPhone 14 Pro': '2022-09-16',
            'iPhone 14 Plus': '2022-10-07',
            'iPhone 14': '2022-09-16',
            'iPhone 13 Pro Max': '2021-09-24',
            'iPhone 13 Pro': '2021-09-24',
            'iPhone 13 mini': '2021-09-24',
            'iPhone 13': '2021-09-24',
            'iPhone 12 Pro Max': '2020-11-13',
            'iPhone 12 Pro': '2020-10-23',
            'iPhone 12 mini': '2020-11-13',
            'iPhone 12': '2020-10-23',
            'iPhone SE': '2022-03-18',
            'iPhone 11': '2019-09-20',
            'iPhone XR': '2018-10-26',
            
            # Samsung Galaxy models
            'Samsung Galaxy S24 Ultra': '2024-01-24',
            'Samsung Galaxy S24+': '2024-01-24',
            'Samsung Galaxy S24': '2024-01-24',
            'Samsung Galaxy S23 Ultra': '2023-02-17',
            'Samsung Galaxy S23+': '2023-02-17',
            'Samsung Galaxy S23': '2023-02-17',
            'Samsung Galaxy S22': '2022-02-25',
            'Samsung Galaxy A54': '2023-03-24',
            'Samsung Galaxy A34': '2023-03-24',
            'Samsung Galaxy A53': '2022-03-17',
            
            # Google Pixel models
            'Google Pixel 8 Pro': '2023-10-12',
            'Google Pixel 8': '2023-10-12',
            'Google Pixel 7 Pro': '2022-10-13',
            'Google Pixel 7': '2022-10-13',
            'Google Pixel 6a': '2022-07-28',
            'Google Pixel 6': '2021-10-28',
            
            # Other popular models
            'OnePlus 11': '2023-02-07',
            'OnePlus 10 Pro': '2022-03-31',
            'Xiaomi 13': '2022-12-11',
            'Xiaomi 12': '2021-12-28',
            'Huawei P50': '2021-07-29',
            'Huawei P40': '2020-03-26'
        }
        
        features = {}
        device_model = str(user_device[device_model_col])
        current_date = datetime.now()
        
        # Get device release date
        if device_model in device_release_dates:
            release_date = datetime.strptime(device_release_dates[device_model], '%Y-%m-%d')
            device_age_months = (current_date - release_date).days / 30.44
        else:
            # Default age for unknown devices (assume 24 months)
            device_age_months = 24
        
        features['device_age_months'] = round(device_age_months, 1)
        
        # Device generation score (newer = higher score)
        if device_age_months <= 12:
            features['device_generation_score'] = 5  # Latest generation
        elif device_age_months <= 24:
            features['device_generation_score'] = 4  # Recent generation
        elif device_age_months <= 36:
            features['device_generation_score'] = 3  # Moderate generation
        elif device_age_months <= 48:
            features['device_generation_score'] = 2  # Older generation
        else:
            features['device_generation_score'] = 1  # Very old generation
        
        # Premium device indicator
        premium_models = [
            'iPhone 14 Pro', 'iPhone 14 Pro Max', 'iPhone 13 Pro', 'iPhone 13 Pro Max',
            'Samsung Galaxy S24 Ultra', 'Samsung Galaxy S23 Ultra', 'Samsung Galaxy S22 Ultra',
            'Google Pixel 8 Pro', 'Google Pixel 7 Pro', 'OnePlus 11'
        ]
        features['is_premium_device'] = 1 if any(premium in device_model for premium in premium_models) else 0
        
        # Device value tier (1-5, higher = more expensive)
        if features['is_premium_device']:
            features['device_value_tier'] = 5
        elif any(model in device_model for model in ['iPhone', 'Galaxy S', 'Pixel']):
            features['device_value_tier'] = 4
        elif any(model in device_model for model in ['Galaxy A', 'OnePlus', 'Xiaomi']):
            features['device_value_tier'] = 3
        else:
            features['device_value_tier'] = 2
        
        # OS age estimation
        if 'iPhone' in device_model:
            features['os_age_months'] = max(0, device_age_months - 6)  # iOS updates lag slightly
        else:
            features['os_age_months'] = max(0, device_age_months - 3)  # Android updates vary
        
        return features
    
    def _calculate_app_ecosystem(self, user_device, app_list_col):
        """Calculate app ecosystem features focusing on financial and security apps."""
        features = {}
        
        if app_list_col and app_list_col in user_device.index and pd.notna(user_device[app_list_col]):
            # Parse app list (assuming comma-separated or list format)
            if isinstance(user_device[app_list_col], str):
                apps = [app.strip().lower() for app in user_device[app_list_col].split(',')]
            elif isinstance(user_device[app_list_col], list):
                apps = [app.lower() for app in user_device[app_list_col]]
            else:
                apps = []
        else:
            apps = []
        
        # Financial app keywords
        financial_keywords = [
            'bank', 'banking', 'finance', 'money', 'wallet', 'pay', 'payment',
            'credit', 'loan', 'invest', 'trading', 'crypto', 'bitcoin',
            'paypal', 'venmo', 'zelle', 'cashapp', 'robinhood', 'mint',
            'quicken', 'budget', 'expense', 'tax', 'accounting'
        ]
        
        # Security app keywords
        security_keywords = [
            'security', 'antivirus', 'vpn', 'password', 'authenticator',
            'secure', 'privacy', 'protection', 'firewall', 'encryption',
            'norton', 'mcafee', 'kaspersky', 'lastpass', 'bitwarden',
            '1password', 'authy', 'google authenticator'
        ]
        
        # Productivity app keywords
        productivity_keywords = [
            'office', 'word', 'excel', 'powerpoint', 'pdf', 'document',
            'note', 'calendar', 'email', 'task', 'project', 'productivity',
            'microsoft', 'google', 'adobe', 'slack', 'teams', 'zoom'
        ]
        
        # Count apps by category
        financial_count = sum(1 for app in apps if any(keyword in app for keyword in financial_keywords))
        security_count = sum(1 for app in apps if any(keyword in app for keyword in security_keywords))
        productivity_count = sum(1 for app in apps if any(keyword in app for keyword in productivity_keywords))
        
        total_apps = len(apps) if apps else 1  # Avoid division by zero
        
        features['financial_apps_count'] = financial_count
        features['security_apps_count'] = security_count
        features['productivity_apps_count'] = productivity_count
        features['total_app_categories'] = len(set([
            cat for cat, count in [
                ('financial', financial_count),
                ('security', security_count),
                ('productivity', productivity_count)
            ] if count > 0
        ]))
        
        # App ratios
        features['financial_app_ratio'] = financial_count / total_apps
        features['security_app_ratio'] = security_count / total_apps
        
        # App sophistication score (0-10)
        sophistication = (
            min(financial_count, 3) * 2 +  # Financial apps worth 2 points each (max 6)
            min(security_count, 2) * 2 +   # Security apps worth 2 points each (max 4)
            min(productivity_count, 5) * 0.4  # Productivity apps worth 0.4 points each (max 2)
        )
        features['app_sophistication_score'] = min(10, sophistication)
        
        return features
    
    def _calculate_network_behavior(self, user_device, daily_data_col, wifi_data_col, cellular_data_col):
        """Calculate network behavior features."""
        features = {}
        
        # Average daily data consumption
        if daily_data_col and daily_data_col in user_device.index and pd.notna(user_device[daily_data_col]):
            avg_daily_data = float(user_device[daily_data_col])
        else:
            avg_daily_data = 0
        
        features['avg_daily_data_mb'] = avg_daily_data
        
        # WiFi vs Cellular usage ratio
        wifi_data = 0
        cellular_data = 0
        
        if wifi_data_col and wifi_data_col in user_device.index and pd.notna(user_device[wifi_data_col]):
            wifi_data = float(user_device[wifi_data_col])
        
        if cellular_data_col and cellular_data_col in user_device.index and pd.notna(user_device[cellular_data_col]):
            cellular_data = float(user_device[cellular_data_col])
        
        # Calculate WiFi to cellular ratio
        if cellular_data > 0:
            features['wifi_cellular_ratio'] = wifi_data / cellular_data
        elif wifi_data > 0:
            features['wifi_cellular_ratio'] = 10  # Very high WiFi preference
        else:
            features['wifi_cellular_ratio'] = 1  # Default neutral ratio
        
        # Data usage tier classification
        if avg_daily_data >= 2000:  # > 2GB/day
            features['data_usage_tier'] = 5  # Very heavy user
        elif avg_daily_data >= 1000:  # 1-2GB/day
            features['data_usage_tier'] = 4  # Heavy user
        elif avg_daily_data >= 500:   # 500MB-1GB/day
            features['data_usage_tier'] = 3  # Moderate user
        elif avg_daily_data >= 100:   # 100-500MB/day
            features['data_usage_tier'] = 2  # Light user
        else:                          # < 100MB/day
            features['data_usage_tier'] = 1  # Very light user
        
        # Network efficiency score (preference for WiFi indicates cost consciousness)
        if features['wifi_cellular_ratio'] >= 5:
            efficiency_score = 5  # Very efficient (mostly WiFi)
        elif features['wifi_cellular_ratio'] >= 3:
            efficiency_score = 4  # Efficient
        elif features['wifi_cellular_ratio'] >= 1.5:
            efficiency_score = 3  # Moderate efficiency
        elif features['wifi_cellular_ratio'] >= 0.5:
            efficiency_score = 2  # Low efficiency
        else:
            efficiency_score = 1  # Very low efficiency (mostly cellular)
        
        features['network_efficiency_score'] = efficiency_score
        
        # Data consumption stability (consistent usage patterns)
        total_data = wifi_data + cellular_data
        if total_data > 0 and avg_daily_data > 0:
            # Measure how close monthly total is to 30x daily average
            expected_monthly = avg_daily_data * 30
            stability = 1 - abs(total_data - expected_monthly) / expected_monthly
            features['data_consumption_stability'] = max(0, min(1, stability))
        else:
            features['data_consumption_stability'] = 0
        
        # Preferred network type (0=cellular, 1=balanced, 2=wifi)
        if features['wifi_cellular_ratio'] >= 3:
            features['preferred_network_type'] = 2  # WiFi preferred
        elif features['wifi_cellular_ratio'] >= 0.33:
            features['preferred_network_type'] = 1  # Balanced
        else:
            features['preferred_network_type'] = 0  # Cellular preferred
        
        return features

    def create_all_features(
        self, 
        df: pd.DataFrame,
        previous_loans: Optional[pd.DataFrame] = None,
        polynomial_degree: int = 2
    ) -> pd.DataFrame:
        """
        Create all available features.

        Args:
            df: Input DataFrame
            previous_loans: Optional DataFrame with previous loan information
            polynomial_degree: Degree of polynomial features

        Returns:
            DataFrame with all additional features
        """
        # Create polynomial features
        df = self.create_polynomial_features(df, degree=polynomial_degree)
        
        # Create credit ratios
        df = self.create_credit_ratios(df)
        
        # Create payment ratios if previous loans data is available
        if previous_loans is not None:
            df = self.create_payment_ratios(df, previous_loans)
        
        return df

    def get_feature_names(self) -> Dict[str, List[str]]:
        """
        Get the names of created features grouped by category.

        Returns:
            Dictionary with feature names by category
        """
        return {
            'polynomial': [col for col in self.feature_names 
                         if 'interaction' in col],
            'credit_ratios': [
                'CREDIT_INCOME_PERCENT',
                'ANNUITY_INCOME_PERCENT',
                'CREDIT_TERM',
                'DAYS_EMPLOYED_PERCENT'
            ],
            'payment_ratios': ['PAYMENT_RATIO'],
            'digital_footprint': [
                # Transaction Frequency Features
                'total_transactions',
                'avg_monthly_transactions',
                'std_monthly_transactions',
                'max_monthly_transactions',
                'min_monthly_transactions',
                'avg_days_between_transactions',
                
                # Transaction Value Features
                'avg_transaction_value',
                'median_transaction_value',
                'std_transaction_value',
                'max_transaction_value',
                'min_transaction_value',
                'total_transaction_value',
                'avg_monthly_spending',
                'std_monthly_spending',
                
                # Spending Pattern Features
                'essential_spending_total',
                'essential_spending_avg',
                'essential_transaction_count',
                'discretionary_spending_total',
                'discretionary_spending_avg',
                'discretionary_transaction_count',
                'essential_discretionary_ratio',
                'essential_spending_pct',
                'discretionary_spending_pct',
                'total_user_spending',
                
                # Behavioral Features
                'unique_categories',
                'transaction_span_days',
                'time_consistency',
                'day_consistency'
            ],
            'utility_telecom': [
                # Payment Consistency Features
                'avg_monthly_payment',
                'std_monthly_payment',
                'payment_consistency_cv',
                'payment_stability_score',
                'payment_range',
                'payment_months_count',
                
                # Tenure Features
                'tenure_days',
                'tenure_months',
                'tenure_years',
                'tenure_category',
                
                # Usage Volatility Features
                'avg_usage',
                'std_usage',
                'usage_cv',
                'usage_volatility_3m',
                'max_usage_volatility_3m',
                'usage_range',
                'usage_trend_slope',
                'usage_consistency_score',
                
                # Payment Behavior Features
                'total_payments',
                'payment_span_days',
                'avg_days_between_payments',
                'payment_regularity_score',
                
                # Service Features
                'unique_services_count',
                'service_engagement_score',
                'primary_service_type',
                
                # Overall Score
                'utility_stability_score'
            ],
            'mobility': [
                # Location Stability Features
                'unique_towers_count',
                'unique_networks_count',
                'primary_tower_frequency',
                'primary_network_frequency',
                'location_stability_score',
                'tower_consistency_ratio',
                'network_consistency_ratio',
                
                # Work-Home Consistency Features
                'home_location_lat',
                'home_location_lon',
                'work_location_lat', 
                'work_location_lon',
                'home_work_distance_km',
                'commute_consistency_score',
                'location_transition_count',
                'work_home_travel_frequency',
                'location_pattern_regularity',
                
                # Travel Radius Features
                'centroid_lat',
                'centroid_lon',
                'radius_of_gyration_km',
                'max_distance_from_centroid_km',
                'avg_distance_from_centroid_km',
                'mobility_range_95th_percentile',
                'geographic_spread',
                'movement_entropy',
                'travel_radius_stability'
            ],
            'device': [
                # Device Age Proxy Features
                'device_age_months',
                'device_generation_score',
                'is_premium_device',
                'device_value_tier',
                'os_age_months',
                
                # App Ecosystem Features
                'financial_apps_count',
                'security_apps_count',
                'productivity_apps_count',
                'total_app_categories',
                'financial_app_ratio',
                'security_app_ratio',
                'app_sophistication_score',
                
                # Network Behavior Features
                'avg_daily_data_mb',
                'wifi_cellular_ratio',
                'data_usage_tier',
                'network_efficiency_score',
                'data_consumption_stability',
                'preferred_network_type'
            ]
        }
