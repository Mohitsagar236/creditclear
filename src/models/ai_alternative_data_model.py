"""
Advanced AI/ML Model for Alternative Data Credit Risk Assessment

This module implements a comprehensive AI model that automatically detects and processes
alternative data from user devices to calculate credit risk using traditional Kaggle data
combined with modern digital footprint analytics.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import roc_auc_score, classification_report
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.neural_network import MLPClassifier
    import xgboost as xgb
    import lightgbm as lgb
    SKLEARN_AVAILABLE = True
except ImportError:
    warnings.warn("Machine learning libraries not available. Using mock implementation.")
    SKLEARN_AVAILABLE = False

from .base_model import BaseModel

logger = logging.getLogger(__name__)


class AIAlternativeDataModel(BaseModel):
    """
    Advanced AI model for alternative data credit risk assessment.
    
    This model combines traditional credit data with modern alternative data sources
    including device analytics, digital footprint, behavioral patterns, and location data.
    """
    
    def __init__(self, random_state: int = 42):
        """Initialize the AI Alternative Data Model."""
        super().__init__("ai_alternative_data", random_state)
        
        # Model components
        self.primary_model = None  # Main XGBoost model
        self.secondary_model = None  # Neural network for complex patterns
        self.device_risk_model = None  # Specialized device risk scoring
        self.behavioral_model = None  # Behavioral pattern analysis
        
        # Data processors
        self.scaler = StandardScaler()
        self.feature_selector = SelectKBest(f_classif, k=50)
        self.label_encoders = {}
        
        # Feature importance tracking
        self.feature_importance_scores = {}
        self.alternative_data_weights = {}
        
        # Risk assessment thresholds
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.8
        }
        
    def preprocess_kaggle_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess Kaggle Home Credit data with advanced feature engineering.
        
        Args:
            df: Raw Kaggle data
            
        Returns:
            Processed DataFrame with engineered features
        """
        logger.info("Preprocessing Kaggle Home Credit data...")
        
        # Create a copy to avoid modifying original data
        processed_df = df.copy()
        
        # Handle missing values intelligently
        numeric_columns = processed_df.select_dtypes(include=[np.number]).columns
        categorical_columns = processed_df.select_dtypes(include=['object']).columns
        
        # Fill missing values
        for col in numeric_columns:
            if processed_df[col].isnull().sum() > 0:
                processed_df[col].fillna(processed_df[col].median(), inplace=True)
                
        for col in categorical_columns:
            if processed_df[col].isnull().sum() > 0:
                processed_df[col].fillna('Unknown', inplace=True)
        
        # Advanced feature engineering
        if 'AMT_INCOME_TOTAL' in processed_df.columns and 'AMT_CREDIT' in processed_df.columns:
            # Credit to income ratio
            processed_df['CREDIT_INCOME_RATIO'] = processed_df['AMT_CREDIT'] / (processed_df['AMT_INCOME_TOTAL'] + 1)
            
            # Income per family member
            if 'CNT_FAM_MEMBERS' in processed_df.columns:
                processed_df['INCOME_PER_MEMBER'] = processed_df['AMT_INCOME_TOTAL'] / (processed_df['CNT_FAM_MEMBERS'] + 1)
        
        if 'AMT_ANNUITY' in processed_df.columns and 'AMT_CREDIT' in processed_df.columns:
            # Annuity to credit ratio
            processed_df['ANNUITY_CREDIT_RATIO'] = processed_df['AMT_ANNUITY'] / (processed_df['AMT_CREDIT'] + 1)
        
        if 'DAYS_BIRTH' in processed_df.columns:
            # Convert to age
            processed_df['AGE_YEARS'] = abs(processed_df['DAYS_BIRTH']) / 365.25
            processed_df['AGE_GROUP'] = pd.cut(processed_df['AGE_YEARS'], 
                                             bins=[0, 25, 35, 45, 55, 100], 
                                             labels=['Young', 'YoungAdult', 'MiddleAge', 'Mature', 'Senior'])
        
        if 'DAYS_EMPLOYED' in processed_df.columns:
            # Employment stability
            processed_df['EMPLOYMENT_YEARS'] = abs(processed_df['DAYS_EMPLOYED']) / 365.25
            processed_df['EMPLOYMENT_STABILITY'] = processed_df['EMPLOYMENT_YEARS'].apply(
                lambda x: 'Stable' if x > 2 else 'Unstable' if x > 0 else 'Unemployed'
            )
        
        # Create credit history features
        external_source_cols = [col for col in processed_df.columns if 'EXT_SOURCE' in col]
        if external_source_cols:
            processed_df['EXT_SOURCE_MEAN'] = processed_df[external_source_cols].mean(axis=1)
            processed_df['EXT_SOURCE_STD'] = processed_df[external_source_cols].std(axis=1)
            processed_df['EXT_SOURCE_MAX'] = processed_df[external_source_cols].max(axis=1)
            processed_df['EXT_SOURCE_MIN'] = processed_df[external_source_cols].min(axis=1)
        
        # Encode categorical variables
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                processed_df[col] = self.label_encoders[col].fit_transform(processed_df[col].astype(str))
            else:
                # Handle unseen labels
                le = self.label_encoders[col]
                processed_df[col] = processed_df[col].astype(str)
                mask = processed_df[col].isin(le.classes_)
                processed_df.loc[mask, col] = le.transform(processed_df.loc[mask, col])
                processed_df.loc[~mask, col] = -1  # Assign -1 to unseen labels
        
        logger.info(f"Kaggle data preprocessing complete. Shape: {processed_df.shape}")
        return processed_df
    
    def extract_device_features(self, device_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract features from device analytics data.
        
        Args:
            device_data: Device analytics profile
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # Device stability features
            device_info = device_data.get('device', {})
            features['device_age_estimated'] = self._estimate_device_age(device_info.get('model', ''))
            features['os_version_score'] = self._score_os_version(
                device_info.get('platform', ''), 
                device_info.get('systemVersion', '')
            )
            features['device_security_score'] = float(device_info.get('isPinOrFingerprintSet', False))
            
            # Hardware features
            features['total_memory_gb'] = device_info.get('totalMemory', 0) / (1024**3)
            features['available_storage_gb'] = device_info.get('totalDiskCapacity', 0) / (1024**3)
            features['is_tablet'] = float(device_info.get('isTablet', False))
            
            # Network features
            network_info = device_data.get('network', {})
            features['is_wifi_connected'] = float(network_info.get('type') == 'wifi')
            features['connection_stability'] = float(network_info.get('isInternetReachable', False))
            features['expensive_connection'] = float(network_info.get('details', {}).get('isConnectionExpensive', False))
            
            # Risk flags
            risk_flags = device_data.get('riskFlags', {})
            features['emulator_risk'] = float(risk_flags.get('isEmulator', False)) * 100
            features['rooted_risk'] = float(risk_flags.get('isRooted', False)) * 100
            features['jailbroken_risk'] = float(risk_flags.get('isJailbroken', False)) * 100
            features['debugging_risk'] = float(risk_flags.get('isDebuggingEnabled', False)) * 50
            
            # App ecosystem features
            apps_info = device_data.get('apps', {})
            features['financial_apps_count'] = apps_info.get('totalCount', 0)
            features['banking_apps_count'] = len(apps_info.get('banking', []))
            features['investment_apps_count'] = len(apps_info.get('investment', []))
            features['lending_apps_count'] = len(apps_info.get('lending', []))
            
        except Exception as e:
            logger.warning(f"Error extracting device features: {e}")
            # Return zero features if extraction fails
            for key in ['device_age_estimated', 'os_version_score', 'device_security_score',
                       'total_memory_gb', 'available_storage_gb', 'is_tablet',
                       'is_wifi_connected', 'connection_stability', 'expensive_connection',
                       'emulator_risk', 'rooted_risk', 'jailbroken_risk', 'debugging_risk',
                       'financial_apps_count', 'banking_apps_count', 'investment_apps_count', 'lending_apps_count']:
                features[key] = 0.0
        
        return features
    
    def extract_behavioral_features(self, alternative_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract behavioral pattern features from alternative data sources.
        
        Args:
            alternative_data: Alternative data including location, utility, digital footprint
            
        Returns:
            Dictionary of behavioral features
        """
        features = {}
        
        try:
            # Location-based features
            location_data = alternative_data.get('location', {})
            features['location_consistency'] = self._score_location_consistency(location_data)
            features['travel_pattern_score'] = self._score_travel_patterns(location_data)
            
            # Utility payment features
            utility_data = alternative_data.get('utility', {})
            features['utility_payment_score'] = self._score_utility_payments(utility_data)
            features['subscription_count'] = self._count_subscriptions(utility_data)
            
            # Digital footprint features
            digital_data = alternative_data.get('digitalFootprint', {})
            features['social_media_presence'] = self._score_social_presence(digital_data)
            features['online_activity_score'] = self._score_online_activity(digital_data)
            features['digital_identity_score'] = self._score_digital_identity(digital_data)
            
            # Communication patterns
            communication_data = alternative_data.get('communication', {})
            features['contact_stability'] = self._score_contact_stability(communication_data)
            features['communication_frequency'] = self._score_communication_frequency(communication_data)
            
        except Exception as e:
            logger.warning(f"Error extracting behavioral features: {e}")
            # Return default features if extraction fails
            for key in ['location_consistency', 'travel_pattern_score', 'utility_payment_score',
                       'subscription_count', 'social_media_presence', 'online_activity_score',
                       'digital_identity_score', 'contact_stability', 'communication_frequency']:
                features[key] = 50.0  # Neutral scores
        
        return features
    
    def _estimate_device_age(self, device_model: str) -> float:
        """Estimate device age based on model name."""
        if not device_model:
            return 2.0  # Default age
            
        model_lower = device_model.lower()
        
        # iPhone age estimation
        if 'iphone' in model_lower:
            if any(version in model_lower for version in ['15', '14', '13']):
                return 0.5
            elif any(version in model_lower for version in ['12', '11']):
                return 1.5
            elif any(version in model_lower for version in ['x', '8', '7']):
                return 3.0
            else:
                return 5.0
        
        # Android age estimation
        if any(brand in model_lower for brand in ['samsung', 'galaxy']):
            if any(model in model_lower for model in ['s23', 's22', 's21']):
                return 0.5
            elif any(model in model_lower for model in ['s20', 's10']):
                return 2.0
            else:
                return 4.0
        
        return 2.5  # Default for unknown devices
    
    def _score_os_version(self, platform: str, version: str) -> float:
        """Score OS version for security and modernity."""
        if not platform or not version:
            return 50.0
            
        try:
            major_version = int(version.split('.')[0])
            
            if platform.lower() == 'ios':
                if major_version >= 16:
                    return 95.0
                elif major_version >= 14:
                    return 80.0
                elif major_version >= 12:
                    return 60.0
                else:
                    return 30.0
            
            elif platform.lower() == 'android':
                if major_version >= 13:
                    return 95.0
                elif major_version >= 11:
                    return 80.0
                elif major_version >= 9:
                    return 60.0
                else:
                    return 30.0
        
        except (ValueError, IndexError):
            pass
        
        return 50.0  # Default score
    
    def _score_location_consistency(self, location_data: Dict) -> float:
        """Score location consistency and stability."""
        if not location_data:
            return 50.0
        
        consistency_score = 0.0
        
        # Home location stability
        if location_data.get('homeLocation') == 'detected':
            consistency_score += 30.0
        
        # Work location stability
        if location_data.get('workLocation') == 'detected':
            consistency_score += 25.0
        
        # Travel patterns
        travel_pattern = location_data.get('travelPatterns', '')
        if 'regular' in travel_pattern.lower():
            consistency_score += 25.0
        elif 'stable' in travel_pattern.lower():
            consistency_score += 20.0
        
        # Current city verification
        if location_data.get('currentCity'):
            consistency_score += 20.0
        
        return min(consistency_score, 100.0)
    
    def _score_travel_patterns(self, location_data: Dict) -> float:
        """Score travel patterns for risk assessment."""
        if not location_data:
            return 50.0
        
        pattern = location_data.get('travelPatterns', '').lower()
        
        if 'regular_commuter' in pattern:
            return 85.0  # High stability
        elif 'occasional_travel' in pattern:
            return 75.0
        elif 'frequent_travel' in pattern:
            return 40.0  # Higher risk
        elif 'nomadic' in pattern:
            return 25.0  # High risk
        
        return 60.0  # Default
    
    def _score_utility_payments(self, utility_data: Dict) -> float:
        """Score utility payment patterns."""
        if not utility_data:
            return 50.0
        
        score = 0.0
        
        # Mobile recharge patterns
        mobile_pattern = utility_data.get('mobileRecharge', '').lower()
        if 'regular' in mobile_pattern:
            score += 25.0
        elif 'consistent' in mobile_pattern:
            score += 20.0
        
        # Electricity bill payments
        electricity_pattern = utility_data.get('electricityBill', '').lower()
        if 'consistent' in electricity_pattern:
            score += 25.0
        elif 'regular' in electricity_pattern:
            score += 20.0
        
        # Internet usage
        internet_usage = utility_data.get('internetUsage', '').lower()
        if 'high' in internet_usage:
            score += 25.0
        elif 'medium' in internet_usage:
            score += 15.0
        
        # Subscription services
        subscriptions = utility_data.get('subscriptionServices', '').lower()
        if 'multiple' in subscriptions:
            score += 25.0
        elif 'single' in subscriptions:
            score += 15.0
        
        return min(score, 100.0)
    
    def _count_subscriptions(self, utility_data: Dict) -> float:
        """Count active subscription services."""
        if not utility_data:
            return 0.0
        
        subscriptions = utility_data.get('subscriptionServices', '').lower()
        
        if 'multiple' in subscriptions:
            return 5.0  # Estimate multiple subscriptions
        elif 'single' in subscriptions:
            return 1.0
        elif 'none' in subscriptions:
            return 0.0
        
        return 2.0  # Default estimate
    
    def _score_social_presence(self, digital_data: Dict) -> float:
        """Score social media presence."""
        if not digital_data:
            return 30.0
        
        # This would be integrated with actual social media APIs
        # For now, return a moderate score
        return 65.0
    
    def _score_online_activity(self, digital_data: Dict) -> float:
        """Score online activity patterns."""
        if not digital_data:
            return 40.0
        
        # This would analyze browsing patterns, app usage, etc.
        return 70.0
    
    def _score_digital_identity(self, digital_data: Dict) -> float:
        """Score digital identity verification."""
        if not digital_data:
            return 35.0
        
        # This would verify digital identity across platforms
        return 75.0
    
    def _score_contact_stability(self, communication_data: Dict) -> float:
        """Score contact and communication stability."""
        if not communication_data:
            return 50.0
        
        # Analyze contact list stability, communication patterns
        return 70.0
    
    def _score_communication_frequency(self, communication_data: Dict) -> float:
        """Score communication frequency patterns."""
        if not communication_data:
            return 50.0
        
        # Analyze call/message frequency and patterns
        return 65.0
    
    def combine_features(self, kaggle_features: pd.DataFrame, 
                        device_features: Dict[str, float],
                        behavioral_features: Dict[str, float]) -> pd.DataFrame:
        """
        Combine traditional Kaggle features with alternative data features.
        
        Args:
            kaggle_features: Preprocessed Kaggle features
            device_features: Device analytics features
            behavioral_features: Behavioral pattern features
            
        Returns:
            Combined feature DataFrame
        """
        # Convert device and behavioral features to DataFrame
        device_df = pd.DataFrame([device_features])
        behavioral_df = pd.DataFrame([behavioral_features])
        
        # If kaggle_features has multiple rows, broadcast device and behavioral features
        if len(kaggle_features) > 1:
            device_df = pd.concat([device_df] * len(kaggle_features), ignore_index=True)
            behavioral_df = pd.concat([behavioral_df] * len(kaggle_features), ignore_index=True)
        
        # Reset indices to ensure proper concatenation
        kaggle_features = kaggle_features.reset_index(drop=True)
        device_df = device_df.reset_index(drop=True)
        behavioral_df = behavioral_df.reset_index(drop=True)
        
        # Combine all features
        combined_features = pd.concat([kaggle_features, device_df, behavioral_df], axis=1)
        
        # Calculate alternative data importance weights
        total_features = len(combined_features.columns)
        kaggle_weight = len(kaggle_features.columns) / total_features
        device_weight = len(device_df.columns) / total_features
        behavioral_weight = len(behavioral_df.columns) / total_features
        
        self.alternative_data_weights = {
            'kaggle': kaggle_weight,
            'device': device_weight,
            'behavioral': behavioral_weight
        }
        
        logger.info(f"Combined features shape: {combined_features.shape}")
        logger.info(f"Feature weights - Kaggle: {kaggle_weight:.2f}, Device: {device_weight:.2f}, Behavioral: {behavioral_weight:.2f}")
        
        return combined_features
    
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> 'AIAlternativeDataModel':
        """
        Train the AI Alternative Data Model.
        
        Args:
            X: Training features (combined traditional + alternative data)
            y: Training targets
            
        Returns:
            Self for method chaining
        """
        logger.info("Training AI Alternative Data Model...")
        
        # Convert to DataFrame if necessary
        if isinstance(X, np.ndarray):
            X = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(X.shape[1])])
        
        # Store feature names
        self.feature_names = list(X.columns)
        
        # Split into train/validation sets
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=self.random_state, stratify=y)
        
        # Feature selection
        self.feature_selector.fit(X_train, y_train)
        X_train_selected = self.feature_selector.transform(X_train)
        X_val_selected = self.feature_selector.transform(X_val)
        
        # Scale features
        self.scaler.fit(X_train_selected)
        X_train_scaled = self.scaler.transform(X_train_selected)
        X_val_scaled = self.scaler.transform(X_val_selected)
        
        # Train primary XGBoost model
        logger.info("Training primary XGBoost model...")
        self.primary_model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=self.random_state,
            objective='binary:logistic',
            eval_metric='auc'
        )
        self.primary_model.fit(X_train_scaled, y_train)
        
        # Train secondary neural network model
        logger.info("Training secondary neural network model...")
        self.secondary_model = MLPClassifier(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            max_iter=500,
            random_state=self.random_state
        )
        self.secondary_model.fit(X_train_scaled, y_train)
        
        # Train specialized device risk model
        logger.info("Training device risk model...")
        device_feature_indices = [i for i, name in enumerate(self.feature_names) 
                                 if any(keyword in name.lower() for keyword in 
                                       ['device', 'emulator', 'rooted', 'jailbroken', 'security', 'memory', 'tablet'])]
        
        if device_feature_indices:
            X_device = X_train.iloc[:, device_feature_indices]
            self.device_risk_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                random_state=self.random_state
            )
            self.device_risk_model.fit(X_device, y_train)
        
        # Train behavioral model
        logger.info("Training behavioral model...")
        behavioral_feature_indices = [i for i, name in enumerate(self.feature_names) 
                                     if any(keyword in name.lower() for keyword in 
                                           ['location', 'travel', 'utility', 'social', 'digital', 'communication'])]
        
        if behavioral_feature_indices:
            X_behavioral = X_train.iloc[:, behavioral_feature_indices]
            self.behavioral_model = GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=4,
                random_state=self.random_state
            )
            self.behavioral_model.fit(X_behavioral, y_train)
        
        # Evaluate models
        primary_score = roc_auc_score(y_val, self.primary_model.predict_proba(X_val_scaled)[:, 1])
        secondary_score = roc_auc_score(y_val, self.secondary_model.predict_proba(X_val_scaled)[:, 1])
        
        logger.info(f"Primary model AUC: {primary_score:.4f}")
        logger.info(f"Secondary model AUC: {secondary_score:.4f}")
        
        # Store feature importance
        if hasattr(self.primary_model, 'feature_importances_'):
            selected_features = self.feature_selector.get_feature_names_out(self.feature_names)
            self.feature_importance_scores = dict(zip(selected_features, self.primary_model.feature_importances_))
        
        self.is_fitted = True
        logger.info("AI Alternative Data Model training completed!")
        
        return self
    
    def predict_comprehensive_risk(self, kaggle_data: pd.DataFrame,
                                 device_data: Dict[str, Any],
                                 alternative_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make comprehensive risk prediction using all data sources.
        
        Args:
            kaggle_data: Traditional credit data
            device_data: Device analytics data
            alternative_data: Alternative data sources
            
        Returns:
            Comprehensive risk assessment
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
        
        # Preprocess all data sources
        processed_kaggle = self.preprocess_kaggle_data(kaggle_data)
        device_features = self.extract_device_features(device_data)
        behavioral_features = self.extract_behavioral_features(alternative_data)
        
        # Combine features
        combined_features = self.combine_features(processed_kaggle, device_features, behavioral_features)
        
        # Feature selection and scaling
        X_selected = self.feature_selector.transform(combined_features)
        X_scaled = self.scaler.transform(X_selected)
        
        # Get predictions from all models
        primary_prob = self.primary_model.predict_proba(X_scaled)[0, 1]
        secondary_prob = self.secondary_model.predict_proba(X_scaled)[0, 1]
        
        # Device risk assessment
        device_risk_score = 0.5  # Default
        if self.device_risk_model:
            device_feature_indices = [i for i, name in enumerate(combined_features.columns) 
                                     if any(keyword in name.lower() for keyword in 
                                           ['device', 'emulator', 'rooted', 'jailbroken', 'security', 'memory', 'tablet'])]
            if device_feature_indices:
                X_device = combined_features.iloc[:, device_feature_indices]
                device_risk_score = self.device_risk_model.predict_proba(X_device)[0, 1]
        
        # Behavioral risk assessment
        behavioral_risk_score = 0.5  # Default
        if self.behavioral_model:
            behavioral_feature_indices = [i for i, name in enumerate(combined_features.columns) 
                                         if any(keyword in name.lower() for keyword in 
                                               ['location', 'travel', 'utility', 'social', 'digital', 'communication'])]
            if behavioral_feature_indices:
                X_behavioral = combined_features.iloc[:, behavioral_feature_indices]
                behavioral_risk_score = self.behavioral_model.predict_proba(X_behavioral)[0, 1]
        
        # Ensemble prediction with weighted average
        ensemble_score = (
            0.5 * primary_prob +  # Primary model weight
            0.2 * secondary_prob +  # Secondary model weight
            0.15 * device_risk_score +  # Device risk weight
            0.15 * behavioral_risk_score  # Behavioral risk weight
        )
        
        # Determine risk level
        if ensemble_score <= self.risk_thresholds['low']:
            risk_level = 'Low'
        elif ensemble_score <= self.risk_thresholds['medium']:
            risk_level = 'Medium'
        else:
            risk_level = 'High'
        
        # Generate insights and recommendations
        insights = self._generate_insights(device_features, behavioral_features, ensemble_score)
        recommendations = self._generate_recommendations(risk_level, device_features, behavioral_features)
        
        # Calculate confidence based on model agreement
        model_scores = [primary_prob, secondary_prob, device_risk_score, behavioral_risk_score]
        confidence = 1.0 - (np.std(model_scores) / np.mean(model_scores))  # Lower std = higher confidence
        confidence = max(0.5, min(0.99, confidence))  # Bound confidence between 0.5 and 0.99
        
        return {
            'risk_score': ensemble_score,
            'risk_level': risk_level,
            'confidence': confidence,
            'model_scores': {
                'primary_model': primary_prob,
                'secondary_model': secondary_prob,
                'device_risk': device_risk_score,
                'behavioral_risk': behavioral_risk_score
            },
            'insights': insights,
            'recommendations': recommendations,
            'feature_contributions': self._calculate_feature_contributions(combined_features),
            'data_source_weights': self.alternative_data_weights,
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def _generate_insights(self, device_features: Dict, behavioral_features: Dict, risk_score: float) -> List[str]:
        """Generate insights based on feature analysis."""
        insights = []
        
        # Device-based insights
        if device_features.get('emulator_risk', 0) > 50:
            insights.append("⚠️ Device emulation detected - high fraud risk")
        
        if device_features.get('device_security_score', 0) > 0.5:
            insights.append("✓ Device has security features enabled")
        else:
            insights.append("⚠️ Device lacks security features")
        
        if device_features.get('financial_apps_count', 0) > 3:
            insights.append("✓ Multiple financial apps indicate financial engagement")
        
        # Behavioral insights
        if behavioral_features.get('location_consistency', 0) > 70:
            insights.append("✓ Stable location patterns indicate consistency")
        
        if behavioral_features.get('utility_payment_score', 0) > 70:
            insights.append("✓ Regular utility payments show financial responsibility")
        
        if behavioral_features.get('digital_identity_score', 0) > 70:
            insights.append("✓ Strong digital identity verification")
        
        # Overall risk insights
        if risk_score < 0.3:
            insights.append("✓ Low risk profile suitable for standard terms")
        elif risk_score < 0.6:
            insights.append("⚠️ Moderate risk - consider additional verification")
        else:
            insights.append("🚨 High risk profile - enhanced due diligence required")
        
        return insights
    
    def _generate_recommendations(self, risk_level: str, device_features: Dict, behavioral_features: Dict) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if risk_level == 'Low':
            recommendations.extend([
                "Approve with standard terms",
                "Standard monitoring required",
                "Consider for premium product offers"
            ])
        elif risk_level == 'Medium':
            recommendations.extend([
                "Request additional documentation",
                "Implement enhanced monitoring",
                "Consider income verification"
            ])
        else:  # High risk
            recommendations.extend([
                "Require comprehensive verification",
                "Implement strict monitoring",
                "Consider decline or high-risk terms"
            ])
        
        # Device-specific recommendations
        if device_features.get('emulator_risk', 0) > 50:
            recommendations.append("Block application from emulated devices")
        
        if device_features.get('device_security_score', 0) < 0.5:
            recommendations.append("Encourage user to enable device security")
        
        # Behavioral recommendations
        if behavioral_features.get('location_consistency', 0) < 50:
            recommendations.append("Verify address and location information")
        
        if behavioral_features.get('utility_payment_score', 0) < 50:
            recommendations.append("Request utility bill verification")
        
        return recommendations
    
    def _calculate_feature_contributions(self, features: pd.DataFrame) -> Dict[str, float]:
        """Calculate feature contributions to the final prediction."""
        if not hasattr(self.primary_model, 'feature_importances_'):
            return {}
        
        selected_features = self.feature_selector.get_feature_names_out(features.columns)
        contributions = {}
        
        for feature, importance in zip(selected_features, self.primary_model.feature_importances_):
            contributions[feature] = float(importance)
        
        # Sort by importance
        return dict(sorted(contributions.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information."""
        base_info = super().get_model_info()
        
        ai_info = {
            'model_type': 'AI Alternative Data Model',
            'data_sources': ['Kaggle Home Credit', 'Device Analytics', 'Behavioral Data'],
            'algorithms': ['XGBoost', 'Neural Network', 'Random Forest', 'Gradient Boosting'],
            'feature_count': len(self.feature_names) if self.feature_names else 0,
            'alternative_data_weights': self.alternative_data_weights,
            'risk_thresholds': self.risk_thresholds,
            'capabilities': [
                'Traditional credit scoring',
                'Device risk assessment',
                'Behavioral pattern analysis',
                'Digital footprint evaluation',
                'Multi-model ensemble prediction'
            ]
        }
        
        return {**base_info, **ai_info}
