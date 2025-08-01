import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime

class DigitalFootprintModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            # Digital Identity
            'email_verified',
            'phone_verified',
            'account_age_days',
            
            # Social Media
            'social_network_size',
            'social_account_age_days',
            'post_frequency',
            'engagement_rate',
            'connection_growth_rate',
            
            # Mobile Usage
            'daily_app_usage_minutes',
            'finance_apps_count',
            'productive_apps_ratio',
            'active_hours_consistency',
            
            # E-commerce
            'monthly_purchase_frequency',
            'average_order_value',
            'payment_methods_diversity',
            'return_rate',
            
            # Digital Payments
            'monthly_upi_transactions',
            'wallet_usage_frequency',
            'payment_success_rate',
            'payment_time_consistency',
            
            # Utility Services
            'utility_bill_payment_ratio',
            'subscription_services_count',
            'payment_consistency_score',
            
            # Location & Mobility
            'location_stability_score',
            'work_route_consistency',
            'travel_frequency',
            'location_pattern_regularity',
            
            # Device & Technical
            'device_age_months',
            'security_features_enabled',
            'network_stability_score',
            'financial_apps_usage_ratio'
        ]

    def preprocess_data(self, digital_footprint_data):
        """Convert raw digital footprint data into model features"""
        features = []
        for record in digital_footprint_data:
            feature_vector = self._extract_features(record)
            features.append(feature_vector)
        
        return np.array(features)

    def _extract_features(self, record):
        """Extract numerical features from a single digital footprint record"""
        features = []
        
        # Digital Identity features
        features.append(1 if record['digitalIdentity']['emailVerified'] else 0)
        features.append(1 if record['digitalIdentity']['phoneVerified'] else 0)
        features.append(self._calculate_days(record['digitalIdentity']['accountAge']))
        
        # Social Media features
        social = record.get('socialMedia', {})
        features.extend([
            social.get('networkSize', 0),
            self._calculate_days(social.get('accountAge', 0)),
            social.get('activityMetrics', {}).get('postFrequency', 0),
            social.get('activityMetrics', {}).get('engagementRate', 0),
            social.get('activityMetrics', {}).get('connectionGrowth', 0)
        ])
        
        # Mobile Usage features
        mobile = record.get('mobileUsage', {})
        features.extend([
            mobile.get('usageDuration', {}).get('daily', 0),
            len([app for app in mobile.get('appCategories', []) if 'finance' in app.lower()]),
            self._calculate_productive_apps_ratio(mobile.get('appCategories', [])),
            self._calculate_active_hours_consistency(mobile.get('activeHours', []))
        ])
        
        # Add remaining feature calculations...
        
        return np.array(features)

    def build_model(self):
        """Create the neural network model"""
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu', input_shape=(len(self.feature_columns),)),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(32, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(16, activation='relu'),
            tf.keras.layers.Dense(1, activation='sigmoid')
        ])
        
        self.model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy', tf.keras.metrics.AUC()]
        )

    def train(self, X_train, y_train, validation_split=0.2, epochs=50, batch_size=32):
        """Train the model on digital footprint data"""
        if self.model is None:
            self.build_model()
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Train the model
        history = self.model.fit(
            X_scaled,
            y_train,
            validation_split=validation_split,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True
                )
            ]
        )
        
        return history

    def predict_risk(self, digital_footprint_data):
        """Predict credit risk based on digital footprint"""
        features = self.preprocess_data([digital_footprint_data])
        features_scaled = self.scaler.transform(features)
        
        risk_score = self.model.predict(features_scaled)[0][0]
        
        # Generate insights based on feature importance
        insights = self._generate_insights(features[0], risk_score)
        
        return {
            'risk_score': float(risk_score),
            'risk_level': self._get_risk_level(risk_score),
            'insights': insights,
            'confidence': self._calculate_confidence(features[0]),
            'recommendations': self._generate_recommendations(features[0], risk_score)
        }

    def _get_risk_level(self, risk_score):
        """Convert risk score to risk level"""
        if risk_score < 0.2:
            return 'very_low'
        elif risk_score < 0.4:
            return 'low'
        elif risk_score < 0.6:
            return 'moderate'
        elif risk_score < 0.8:
            return 'high'
        else:
            return 'very_high'

    def _generate_insights(self, features, risk_score):
        """Generate insights based on feature importance"""
        insights = []
        
        # Map features to their importance scores
        feature_importance = list(zip(self.feature_columns, features))
        
        # Sort by absolute importance
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # Generate insights for top features
        for feature, value in feature_importance[:5]:
            if value > 0.7:
                insights.append(f"Strong positive signal from {feature.replace('_', ' ')}")
            elif value < 0.3:
                insights.append(f"Potential concern with {feature.replace('_', ' ')}")
        
        return insights

    def _generate_recommendations(self, features, risk_score):
        """Generate recommendations based on feature values and risk score"""
        recommendations = []
        
        # Example recommendation logic
        if risk_score > 0.6:
            if features[self.feature_columns.index('payment_consistency_score')] < 0.5:
                recommendations.append("Improve payment consistency across utilities and subscriptions")
            if features[self.feature_columns.index('financial_apps_usage_ratio')] < 0.3:
                recommendations.append("Consider using more financial management apps")
            if features[self.feature_columns.index('location_stability_score')] < 0.4:
                recommendations.append("Maintain more consistent location patterns")
        
        return recommendations

    def _calculate_confidence(self, features):
        """Calculate confidence score for the prediction"""
        # Example confidence calculation based on data completeness
        non_zero_features = sum(1 for f in features if f != 0)
        return min(1.0, non_zero_features / len(features))

    # Helper methods
    def _calculate_days(self, date_str):
        """Calculate days from a date string"""
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return (datetime.now() - date).days
        except:
            return 0

    def _calculate_productive_apps_ratio(self, app_categories):
        """Calculate ratio of productive apps"""
        if not app_categories:
            return 0
        productive_categories = {'finance', 'productivity', 'business', 'education'}
        productive_count = sum(1 for cat in app_categories if cat.lower() in productive_categories)
        return productive_count / len(app_categories)

    def _calculate_active_hours_consistency(self, active_hours):
        """Calculate consistency score for active hours"""
        if not active_hours:
            return 0
        # Simple consistency score based on number of regular active hours
        return min(1.0, len(active_hours) / 24)
