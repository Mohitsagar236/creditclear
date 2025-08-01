"""
XGBoost model implementation for credit risk prediction.

This module implements a wrapper class for XGBoost classifier
specifically configured for credit risk prediction tasks.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Optional, Union, Dict, Any

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    warnings.warn("XGBoost not available. Using mock implementation.")
    from ..utils.mock_ml import get_mock_xgboost
    xgb = get_mock_xgboost()
    XGBClassifier = xgb.XGBRegressor  # Use regressor as classifier mock
    XGBOOST_AVAILABLE = False

try:
    from sklearn.base import BaseEstimator
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    warnings.warn("Scikit-learn not available. Using mock implementation.")
    
    class BaseEstimator:
        """Mock BaseEstimator."""
        pass
    
    def train_test_split(*args, **kwargs):
        """Mock train_test_split."""
        X, y = args[0], args[1]
        split_idx = int(len(X) * 0.8)
        return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:]
    
    SKLEARN_AVAILABLE = False


class XGBoostModel(BaseEstimator):
    """XGBoost classifier for credit risk prediction.
    
    This class implements a wrapper around XGBoost's classifier with specific
    configurations for credit risk prediction, including handling of imbalanced data.
    """
    
    def __init__(
        self,
        n_estimators: int = 1000,
        max_depth: int = 6,
        learning_rate: float = 0.01,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 1,
        reg_alpha: float = 0.1,
        reg_lambda: float = 1.0,
        random_state: int = 42,
        **kwargs
    ):
        """Initialize XGBoost model with credit risk specific parameters.
        
        Args:
            n_estimators: Number of boosting rounds
            max_depth: Maximum tree depth
            learning_rate: Learning rate for gradient boosting
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns when constructing each tree
            min_child_weight: Minimum sum of instance weight needed in a child
            reg_alpha: L1 regularization term on weights
            reg_lambda: L2 regularization term on weights
            random_state: Random seed for reproducibility
            **kwargs: Additional parameters for XGBClassifier
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_weight = min_child_weight
        self.reg_alpha = reg_alpha
        self.reg_lambda = reg_lambda
        self.random_state = random_state
        self.additional_params = kwargs
        
        # Initialize the model
        self.model = None
        self.is_fitted = False
        self.feature_names = None
        
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> 'XGBoostModel':
        """Fit the XGBoost model to training data.
        
        Args:
            X: Training features
            y: Training target variable
            
        Returns:
            Self for method chaining
        """
        # Convert to appropriate format
        if isinstance(X, pd.DataFrame):
            self.feature_names = X.columns.tolist()
            X = X.values
        else:
            self.feature_names = [f"feature_{i}" for i in range(X.shape[1])]
            
        if isinstance(y, pd.Series):
            y = y.values
            
        # Initialize model with parameters
        self.model = XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            min_child_weight=self.min_child_weight,
            reg_alpha=self.reg_alpha,
            reg_lambda=self.reg_lambda,
            random_state=self.random_state,
            objective='binary:logistic',
            eval_metric='logloss',
            **self.additional_params
        )
        
        # Fit the model
        self.model.fit(X, y)
        self.is_fitted = True
        
        return self
        
    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Make predictions on new data.
        
        Args:
            X: Features for prediction
            
        Returns:
            Binary predictions (0 or 1)
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert to appropriate format
        if isinstance(X, pd.DataFrame):
            X = X.values
            
        return self.model.predict(X)
        
    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """Predict class probabilities.
        
        Args:
            X: Features for prediction
            
        Returns:
            Array of shape (n_samples, 2) with probabilities for each class
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        # Convert to appropriate format
        if isinstance(X, pd.DataFrame):
            X = X.values
            
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            # For mock implementation, create probabilities from predictions
            preds = self.model.predict(X)
            return np.column_stack([1 - preds, preds])
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
            
        Raises:
            ValueError: If model hasn't been fitted yet
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before getting feature importance")
            
        if hasattr(self.model, 'feature_importances_'):
            importance_scores = self.model.feature_importances_
        else:
            # For mock implementation, return random importances
            importance_scores = np.random.random(len(self.feature_names))
            
        return dict(zip(self.feature_names, importance_scores))
        
    def get_params(self, deep: bool = True) -> Dict[str, Any]:
        """Get model parameters.
        
        Args:
            deep: Whether to return parameters of sub-estimators
            
        Returns:
            Dictionary of parameters
        """
        params = {
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'learning_rate': self.learning_rate,
            'subsample': self.subsample,
            'colsample_bytree': self.colsample_bytree,
            'min_child_weight': self.min_child_weight,
            'reg_alpha': self.reg_alpha,
            'reg_lambda': self.reg_lambda,
            'random_state': self.random_state,
        }
        params.update(self.additional_params)
        return params
        
    def set_params(self, **params) -> 'XGBoostModel':
        """Set model parameters.
        
        Args:
            **params: Parameters to set
            
        Returns:
            Self for method chaining
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                self.additional_params[key] = value
                
        # Reset fitted status if parameters change
        self.is_fitted = False
        self.model = None
        
        return self
