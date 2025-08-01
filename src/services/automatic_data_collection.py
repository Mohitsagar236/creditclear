"""
Automatic Alternative Data Collection Service

This service automatically collects and integrates alternative data from various sources
including device analytics, behavioral patterns, digital footprint, and location data
for comprehensive credit risk assessment.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json
import pandas as pd
from pathlib import Path

from ..models.ai_alternative_data_model import AIAlternativeDataModel
from ..utils.data_loader import load_kaggle_data

logger = logging.getLogger(__name__)


class AutomaticDataCollectionService:
    """
    Service for automatic collection and integration of alternative data sources.
    
    This service orchestrates the collection of:
    - Device analytics data
    - Location and mobility patterns
    - Digital footprint information
    - Utility and payment behaviors
    - Communication patterns
    - Traditional credit data from Kaggle
    """
    
    def __init__(self):
        """Initialize the automatic data collection service."""
        self.ai_model = AIAlternativeDataModel()
        self.collection_timestamp = None
        self.cached_kaggle_data = None
        self.data_sources_status = {
            'kaggle_data': False,
            'device_analytics': False,
            'location_data': False,
            'utility_data': False,
            'digital_footprint': False,
            'communication_data': False
        }
        
        # Data quality thresholds
        self.quality_thresholds = {
            'minimum_features': 20,
            'required_device_features': 10,
            'required_behavioral_features': 5
        }
        
    async def initialize_service(self) -> bool:
        """
        Initialize the service and load base data.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            logger.info("Initializing Automatic Data Collection Service...")
            
            # Load Kaggle base data
            await self._load_kaggle_base_data()
            
            # Initialize AI model if not already done
            if not self.ai_model.is_fitted:
                await self._train_ai_model()
            
            self.collection_timestamp = datetime.now()
            logger.info("Automatic Data Collection Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize service: {e}")
            return False
    
    async def collect_comprehensive_data(self, user_id: str, device_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatically collect comprehensive alternative data for a user.
        
        Args:
            user_id: Unique identifier for the user
            device_profile: Device analytics profile from mobile app
            
        Returns:
            Dictionary containing all collected data sources
        """
        logger.info(f"Starting comprehensive data collection for user {user_id}")
        
        # Initialize collection results
        collection_results = {
            'user_id': user_id,
            'collection_timestamp': datetime.now().isoformat(),
            'data_sources': {},
            'quality_scores': {},
            'collection_status': 'in_progress'
        }
        
        try:
            # Collect data from all sources in parallel
            collection_tasks = [
                self._collect_device_analytics(device_profile),
                self._collect_location_data(user_id, device_profile),
                self._collect_utility_data(user_id),
                self._collect_digital_footprint(user_id),
                self._collect_communication_data(user_id),
                self._prepare_kaggle_features(user_id)
            ]
            
            # Execute all collections
            results = await asyncio.gather(*collection_tasks, return_exceptions=True)
            
            # Process results
            data_types = ['device_analytics', 'location_data', 'utility_data', 
                         'digital_footprint', 'communication_data', 'kaggle_features']
            
            for i, (data_type, result) in enumerate(zip(data_types, results)):
                if isinstance(result, Exception):
                    logger.error(f"Failed to collect {data_type}: {result}")
                    collection_results['data_sources'][data_type] = {'error': str(result)}
                    collection_results['quality_scores'][data_type] = 0.0
                else:
                    collection_results['data_sources'][data_type] = result
                    collection_results['quality_scores'][data_type] = self._assess_data_quality(data_type, result)
            
            # Calculate overall data quality
            overall_quality = sum(collection_results['quality_scores'].values()) / len(collection_results['quality_scores'])
            collection_results['overall_quality_score'] = overall_quality
            
            # Determine collection status
            if overall_quality >= 0.8:
                collection_results['collection_status'] = 'excellent'
            elif overall_quality >= 0.6:
                collection_results['collection_status'] = 'good'
            elif overall_quality >= 0.4:
                collection_results['collection_status'] = 'acceptable'
            else:
                collection_results['collection_status'] = 'poor'
            
            logger.info(f"Data collection completed for user {user_id} with {collection_results['collection_status']} quality")
            
            return collection_results
            
        except Exception as e:
            logger.error(f"Error in comprehensive data collection: {e}")
            collection_results['collection_status'] = 'failed'
            collection_results['error'] = str(e)
            return collection_results
    
    async def perform_ai_risk_assessment(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform AI-powered risk assessment using all collected data.
        
        Args:
            collected_data: Results from collect_comprehensive_data
            
        Returns:
            Comprehensive risk assessment results
        """
        if not self.ai_model.is_fitted:
            raise ValueError("AI model is not trained")
        
        try:
            logger.info(f"Performing AI risk assessment for user {collected_data['user_id']}")
            
            # Extract data sources
            data_sources = collected_data['data_sources']
            
            # Prepare Kaggle data
            kaggle_data = data_sources.get('kaggle_features', {})
            if 'error' in kaggle_data:
                # Use default/mock data if Kaggle data is not available
                kaggle_data = self._get_default_kaggle_data()
            
            kaggle_df = pd.DataFrame([kaggle_data])
            
            # Prepare device data
            device_data = data_sources.get('device_analytics', {})
            if 'error' in device_data:
                device_data = self._get_default_device_data()
            
            # Prepare alternative data
            alternative_data = {
                'location': data_sources.get('location_data', {}),
                'utility': data_sources.get('utility_data', {}),
                'digitalFootprint': data_sources.get('digital_footprint', {}),
                'communication': data_sources.get('communication_data', {})
            }
            
            # Perform comprehensive risk assessment
            assessment_result = self.ai_model.predict_comprehensive_risk(
                kaggle_data=kaggle_df,
                device_data=device_data,
                alternative_data=alternative_data
            )
            
            # Enhance assessment with collection quality information
            assessment_result['data_collection_quality'] = collected_data['overall_quality_score']
            assessment_result['data_sources_used'] = list(data_sources.keys())
            assessment_result['collection_timestamp'] = collected_data['collection_timestamp']
            
            # Add risk mitigation recommendations based on data quality
            if collected_data['overall_quality_score'] < 0.6:
                assessment_result['recommendations'].insert(0, 
                    "⚠️ Limited data quality - consider additional verification steps")
            
            logger.info(f"AI risk assessment completed: {assessment_result['risk_level']} risk")
            
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in AI risk assessment: {e}")
            raise
    
    async def _collect_device_analytics(self, device_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and process device analytics data."""
        try:
            # Process existing device profile
            processed_device_data = {
                'collection_method': 'react_native_device_info',
                'timestamp': datetime.now().isoformat(),
                **device_profile
            }
            
            # Add additional device insights
            device_insights = self._analyze_device_security(device_profile)
            processed_device_data['security_analysis'] = device_insights
            
            # Calculate device stability score
            stability_score = self._calculate_device_stability(device_profile)
            processed_device_data['stability_score'] = stability_score
            
            return processed_device_data
            
        except Exception as e:
            logger.error(f"Error collecting device analytics: {e}")
            return {'error': str(e)}
    
    async def _collect_location_data(self, user_id: str, device_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Collect location and mobility data."""
        try:
            # Simulate location data collection
            # In a real implementation, this would integrate with location services
            
            location_data = {
                'collection_method': 'gps_and_network',
                'timestamp': datetime.now().isoformat(),
                'current_location': {
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'country': 'India',
                    'coordinates_available': True
                },
                'location_history': {
                    'home_location_detected': True,
                    'work_location_detected': True,
                    'frequent_locations_count': 5
                },
                'mobility_patterns': {
                    'travel_frequency': 'regular_commuter',
                    'average_daily_distance': 25.5,  # km
                    'weekend_vs_weekday_pattern': 'consistent',
                    'long_distance_travel_frequency': 'monthly'
                },
                'location_stability_score': 85.0
            }
            
            return location_data
            
        except Exception as e:
            logger.error(f"Error collecting location data: {e}")
            return {'error': str(e)}
    
    async def _collect_utility_data(self, user_id: str) -> Dict[str, Any]:
        """Collect utility payment and subscription data."""
        try:
            # Simulate utility data collection
            # In a real implementation, this would integrate with utility APIs
            
            utility_data = {
                'collection_method': 'api_integration',
                'timestamp': datetime.now().isoformat(),
                'electricity_payments': {
                    'payment_frequency': 'monthly_regular',
                    'average_bill_amount': 1200,  # INR
                    'payment_timeliness': 'always_on_time',
                    'payment_method': 'auto_debit'
                },
                'mobile_recharge': {
                    'recharge_frequency': 'monthly_regular',
                    'average_recharge_amount': 299,  # INR
                    'recharge_pattern': 'consistent',
                    'data_usage': 'high'
                },
                'internet_services': {
                    'connection_type': 'fiber_broadband',
                    'monthly_bill': 999,  # INR
                    'payment_consistency': 'regular'
                },
                'subscription_services': {
                    'streaming_services': ['Netflix', 'Amazon Prime', 'Spotify'],
                    'total_monthly_subscriptions': 1200,  # INR
                    'subscription_stability': 'stable'
                },
                'utility_reliability_score': 92.0
            }
            
            return utility_data
            
        except Exception as e:
            logger.error(f"Error collecting utility data: {e}")
            return {'error': str(e)}
    
    async def _collect_digital_footprint(self, user_id: str) -> Dict[str, Any]:
        """Collect digital footprint and online behavior data."""
        try:
            # Simulate digital footprint collection
            # In a real implementation, this would integrate with social media APIs
            
            digital_footprint = {
                'collection_method': 'public_api_integration',
                'timestamp': datetime.now().isoformat(),
                'social_media_presence': {
                    'platforms_active': ['LinkedIn', 'Twitter', 'Instagram'],
                    'account_age_average': 5.2,  # years
                    'posting_frequency': 'moderate',
                    'professional_network_size': 250
                },
                'online_shopping_behavior': {
                    'platforms_used': ['Amazon', 'Flipkart', 'Myntra'],
                    'purchase_frequency': 'regular',
                    'average_order_value': 1500,  # INR
                    'payment_method_preference': 'digital'
                },
                'digital_engagement': {
                    'email_activity': 'active',
                    'app_usage_diversity': 'high',
                    'digital_literacy_score': 88.0
                },
                'online_reputation': {
                    'professional_reviews': 'positive',
                    'social_sentiment': 'neutral_positive',
                    'digital_identity_verified': True
                },
                'digital_footprint_score': 82.0
            }
            
            return digital_footprint
            
        except Exception as e:
            logger.error(f"Error collecting digital footprint: {e}")
            return {'error': str(e)}
    
    async def _collect_communication_data(self, user_id: str) -> Dict[str, Any]:
        """Collect communication patterns and contact data."""
        try:
            # Simulate communication data collection
            # In a real implementation, this would require explicit user consent
            
            communication_data = {
                'collection_method': 'user_consent_based',
                'timestamp': datetime.now().isoformat(),
                'contact_patterns': {
                    'contact_list_size': 180,
                    'active_contacts_count': 45,
                    'contact_stability': 'high',
                    'emergency_contacts_available': True
                },
                'communication_frequency': {
                    'daily_calls_average': 8,
                    'daily_messages_average': 25,
                    'communication_consistency': 'regular'
                },
                'network_analysis': {
                    'professional_contacts_ratio': 0.35,
                    'family_contacts_ratio': 0.25,
                    'social_contacts_ratio': 0.40,
                    'network_diversity_score': 75.0
                },
                'communication_reliability_score': 78.0
            }
            
            return communication_data
            
        except Exception as e:
            logger.error(f"Error collecting communication data: {e}")
            return {'error': str(e)}
    
    async def _prepare_kaggle_features(self, user_id: str) -> Dict[str, Any]:
        """Prepare Kaggle-format features for the user."""
        try:
            # In a real implementation, this would map user data to Kaggle format
            # For now, we'll create realistic synthetic data
            
            kaggle_features = {
                'AMT_INCOME_TOTAL': 180000,  # Annual income
                'AMT_CREDIT': 450000,  # Credit amount
                'AMT_ANNUITY': 18500,  # Annuity amount
                'DAYS_BIRTH': -12000,  # Age in days (negative)
                'DAYS_EMPLOYED': -1800,  # Employment length in days
                'CNT_FAM_MEMBERS': 2,  # Family members count
                'NAME_CONTRACT_TYPE': 'Cash loans',
                'CODE_GENDER': 'F',
                'FLAG_OWN_CAR': 'N',
                'FLAG_OWN_REALTY': 'Y',
                'NAME_INCOME_TYPE': 'Working',
                'NAME_EDUCATION_TYPE': 'Higher education',
                'NAME_FAMILY_STATUS': 'Married',
                'NAME_HOUSING_TYPE': 'House / apartment',
                'EXT_SOURCE_1': 0.7,
                'EXT_SOURCE_2': 0.6,
                'EXT_SOURCE_3': 0.8
            }
            
            return kaggle_features
            
        except Exception as e:
            logger.error(f"Error preparing Kaggle features: {e}")
            return {'error': str(e)}
    
    async def _load_kaggle_base_data(self) -> None:
        """Load and cache Kaggle base data."""
        try:
            self.cached_kaggle_data = load_kaggle_data()
            if self.cached_kaggle_data is not None:
                self.data_sources_status['kaggle_data'] = True
                logger.info(f"Loaded Kaggle data with {len(self.cached_kaggle_data)} records")
            else:
                logger.warning("Could not load Kaggle data")
        except Exception as e:
            logger.error(f"Error loading Kaggle data: {e}")
    
    async def _train_ai_model(self) -> None:
        """Train the AI model with available data."""
        try:
            if self.cached_kaggle_data is not None and 'TARGET' in self.cached_kaggle_data.columns:
                # Sample data for training
                sample_size = min(10000, len(self.cached_kaggle_data))
                sample_data = self.cached_kaggle_data.sample(n=sample_size, random_state=42)
                
                # Create mock alternative data for training
                device_features = self.ai_model.extract_device_features(self._get_default_device_data())
                behavioral_features = self.ai_model.extract_behavioral_features({
                    'location': {'homeLocation': 'detected', 'travelPatterns': 'regular_commuter'},
                    'utility': {'mobileRecharge': 'regular', 'electricityBill': 'consistent'},
                    'digitalFootprint': {},
                    'communication': {}
                })
                
                # Prepare training data
                X_kaggle = self.ai_model.preprocess_kaggle_data(sample_data.drop('TARGET', axis=1))
                X_combined = self.ai_model.combine_features(X_kaggle, device_features, behavioral_features)
                y = sample_data['TARGET']
                
                # Train the model
                self.ai_model.fit(X_combined, y)
                logger.info("AI model trained successfully")
            else:
                logger.warning("Cannot train AI model - no suitable data available")
        except Exception as e:
            logger.error(f"Error training AI model: {e}")
    
    def _assess_data_quality(self, data_type: str, data: Dict[str, Any]) -> float:
        """Assess the quality of collected data."""
        if 'error' in data:
            return 0.0
        
        quality_score = 0.0
        
        if data_type == 'device_analytics':
            # Check for key device fields
            required_fields = ['device', 'network', 'riskFlags']
            available_fields = sum(1 for field in required_fields if field in data)
            quality_score = (available_fields / len(required_fields)) * 100
            
        elif data_type == 'location_data':
            # Check for location data completeness
            if 'current_location' in data and 'mobility_patterns' in data:
                quality_score = 85.0
            elif 'current_location' in data:
                quality_score = 60.0
            else:
                quality_score = 30.0
                
        elif data_type in ['utility_data', 'digital_footprint', 'communication_data']:
            # General completeness check
            if isinstance(data, dict) and len(data) > 3:
                quality_score = 80.0
            else:
                quality_score = 50.0
                
        elif data_type == 'kaggle_features':
            # Check for essential Kaggle fields
            essential_fields = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'DAYS_BIRTH']
            available_fields = sum(1 for field in essential_fields if field in data)
            quality_score = (available_fields / len(essential_fields)) * 100
        
        return min(quality_score, 100.0)
    
    def _analyze_device_security(self, device_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze device security characteristics."""
        risk_flags = device_profile.get('riskFlags', {})
        device_info = device_profile.get('device', {})
        
        security_analysis = {
            'security_level': 'medium',
            'risk_factors': [],
            'security_score': 70.0
        }
        
        # Check for high-risk factors
        if risk_flags.get('isEmulator'):
            security_analysis['risk_factors'].append('Emulator detected')
            security_analysis['security_score'] -= 30
            
        if risk_flags.get('isRooted') or risk_flags.get('isJailbroken'):
            security_analysis['risk_factors'].append('Device is rooted/jailbroken')
            security_analysis['security_score'] -= 25
            
        if not risk_flags.get('hasSecurityFeatures'):
            security_analysis['risk_factors'].append('No security features enabled')
            security_analysis['security_score'] -= 15
            
        # Determine security level
        if security_analysis['security_score'] >= 80:
            security_analysis['security_level'] = 'high'
        elif security_analysis['security_score'] >= 60:
            security_analysis['security_level'] = 'medium'
        else:
            security_analysis['security_level'] = 'low'
            
        return security_analysis
    
    def _calculate_device_stability(self, device_profile: Dict[str, Any]) -> float:
        """Calculate device stability score."""
        stability_score = 100.0
        
        device_info = device_profile.get('device', {})
        
        # Check OS version
        platform = device_info.get('platform', '').lower()
        version = device_info.get('systemVersion', '')
        
        if platform == 'android' and version:
            try:
                major_version = int(version.split('.')[0])
                if major_version < 10:
                    stability_score -= 20
            except (ValueError, IndexError):
                stability_score -= 10
                
        elif platform == 'ios' and version:
            try:
                major_version = int(version.split('.')[0])
                if major_version < 14:
                    stability_score -= 20
            except (ValueError, IndexError):
                stability_score -= 10
        
        # Check memory and storage
        total_memory = device_info.get('totalMemory', 0)
        if total_memory < 2 * 1024**3:  # Less than 2GB
            stability_score -= 15
            
        return max(0.0, min(100.0, stability_score))
    
    def _get_default_kaggle_data(self) -> Dict[str, Any]:
        """Get default Kaggle data for fallback."""
        return {
            'AMT_INCOME_TOTAL': 150000,
            'AMT_CREDIT': 300000,
            'AMT_ANNUITY': 15000,
            'DAYS_BIRTH': -10000,
            'DAYS_EMPLOYED': -1500,
            'CNT_FAM_MEMBERS': 2,
            'NAME_CONTRACT_TYPE': 'Cash loans',
            'CODE_GENDER': 'M',
            'FLAG_OWN_CAR': 'N',
            'FLAG_OWN_REALTY': 'Y'
        }
    
    def _get_default_device_data(self) -> Dict[str, Any]:
        """Get default device data for fallback."""
        return {
            'device': {
                'model': 'Unknown',
                'platform': 'Android',
                'systemVersion': '11.0',
                'isPinOrFingerprintSet': False
            },
            'network': {
                'type': 'cellular',
                'isConnected': True
            },
            'riskFlags': {
                'isEmulator': False,
                'isRooted': False,
                'hasSecurityFeatures': False
            },
            'apps': {
                'totalCount': 0,
                'banking': [],
                'investment': [],
                'lending': []
            }
        }


# Global service instance
automatic_data_service = AutomaticDataCollectionService()
