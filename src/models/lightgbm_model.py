"""
LightGBM model implementation for credit risk prediction.

This module implements a wrapper class for LightGBM classifier
specifically configured for credit risk prediction tasks.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Optional, Union, Dict

try:
    from lightgbm import LGBMClassifier
    LIGHTGBM_AVAILABLE = True
except ImportError:
    warnings.warn("LightGBM not available. Using mock implementation.")
    from ..utils.mock_ml import get_mock_lightgbm
    lgb = get_mock_lightgbm()
    LGBMClassifier = lgb.LGBMRegressor  # Use regressor as classifier mock
    LIGHTGBM_AVAILABLE = False

try:
    from sklearn.base import BaseEstimator
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    warnings.warn("Scikit-learn not available. Using mock implementation.")
    from ..utils.mock_ml import get_mock_sklearn
    sklearn_mock = get_mock_sklearn()
    
    class BaseEstimator:
        """Mock BaseEstimator."""
        pass
    
    def train_test_split(*args, **kwargs):
        """Mock train_test_split."""
        X, y = args[0], args[1]
        split_idx = int(len(X) * 0.8)
        return X[:split_idx], X[split_idx:], y[:split_idx], y[split_idx:]
    
    SKLEARN_AVAILABLE = False


class LightGBMModel(BaseEstimator):
    """LightGBM classifier for credit risk prediction.
    
    This class implements a wrapper around LightGBM's classifier with specific
    configurations for credit risk prediction, including handling of imbalanced data.
    """
    
    model_name = "LightGBM Credit Risk Model"
    
    def __init__(
        self,
        n_estimators: int = 1000,
        num_leaves: int = 31,
        learning_rate: float = 0.01,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_samples: int = 20,
        scale_pos_weight: Optional[float] = None,
        early_stopping_rounds: int = 50,
        random_state: int = 42
    ):
        """
        Initialize LightGBM model with credit risk specific parameters.
        
        Args:
            n_estimators: Number of boosting iterations
            num_leaves: Maximum number of leaves in one tree
            learning_rate: Boosting learning rate
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns when constructing trees
            min_child_samples: Minimum number of samples needed in a child
            scale_pos_weight: Weight of positive class for imbalanced datasets
            early_stopping_rounds: Stopping rounds for early stopping
            random_state: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.num_leaves = num_leaves
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_samples = min_child_samples
        self.scale_pos_weight = scale_pos_weight
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        
        self.model = LGBMClassifier(
            n_estimators=n_estimators,
            num_leaves=num_leaves,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            min_child_samples=min_child_samples,
            scale_pos_weight=scale_pos_weight,
            random_state=random_state,
            objective='binary',
            metric='binary_logloss',
            boost_from_average=True,
            force_row_wise=True  # For faster training
        )
        
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        eval_size: float = 0.2,
        **kwargs
    ) -> 'LightGBMModel':
        """
        Fit the LightGBM model to the training data.
        
        Args:
            X: Training features
            y: Target values
            eval_size: Size of evaluation set for early stopping
            **kwargs: Additional arguments to pass to LightGBM's fit method
        
        Returns:
            self: The fitted model
        """
        # Create evaluation set for early stopping
        X_train, X_eval, y_train, y_eval = train_test_split(
            X, y, test_size=eval_size, random_state=self.random_state
        )
        
        # If scale_pos_weight not set, calculate it from data
        if self.scale_pos_weight is None:
            self.scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()
            self.model.set_params(scale_pos_weight=self.scale_pos_weight)
        
        # Fit model with early stopping
        self.model.fit(
            X_train,
            y_train,
            eval_set=[(X_eval, y_eval)],
            eval_metric='binary_logloss',
            early_stopping_rounds=self.early_stopping_rounds,
            verbose=False,
            **kwargs
        )
        
        return self
    
    def predict_proba(
        self,
        X: Union[pd.DataFrame, np.ndarray]
    ) -> np.ndarray:
        """
        Predict class probabilities for X.
        
        Args:
            X: Features to predict
        
        Returns:
            Array of shape (n_samples, 2) with class probabilities
        """
        return self.model.predict_proba(X)
    
    def get_feature_importance(
        self,
        importance_type: str = 'gain'
    ) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Args:
            importance_type: Type of feature importance to calculate
                           ('split', 'gain', or 'weight')
        
        Returns:
            Dictionary mapping feature names to their importance scores
        """
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model hasn't been fitted yet")
        
        # Get feature importance scores
        importance = self.model.booster_.feature_importance(
            importance_type=importance_type
        )
        
        # If we have feature names from training data
        if hasattr(self.model, 'feature_name_'):
            return dict(zip(self.model.feature_name_, importance))
        
        # If we don't have feature names, use indices
        return {f'feature_{i}': imp for i, imp in enumerate(importance)}
