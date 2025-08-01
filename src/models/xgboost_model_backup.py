"""
XGBoost model implementation for credit risk prediction.

This module implements a wrapper class for XGBoost classifier
specifically configured for credit risk prediction tasks.
"""

import warnings
import numpy as np
import pandas as pd
from typing import Optional, Union, Dict

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
    
    SKLEARN_AVAILABLE = Falsemodel implementation for credit risk prediction.

This module implements a wrapper class for XGBoost classifier
specifically configured for credit risk prediction tasks.
"""

import numpy as np
import pandas as pd
from typing import Optional, Union, Dict
from xgboost import XGBClassifier
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split


class XGBoostModel(BaseEstimator):
    """XGBoost classifier for credit risk prediction.
    
    This class implements a wrapper around XGBoost's classifier with specific
    configurations for credit risk prediction, including handling of imbalanced data.
    """
    
    def __init__(
        self,
        n_estimators: int = 1000,
        max_depth: int = 7,
        learning_rate: float = 0.01,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 1,
        scale_pos_weight: Optional[float] = None,
        early_stopping_rounds: int = 50,
        random_state: int = 42
    ):
        """
        Initialize XGBoost model with credit risk specific parameters.
        
        Args:
            n_estimators: Number of gradient boosted trees
            max_depth: Maximum tree depth
            learning_rate: Boosting learning rate
            subsample: Subsample ratio of training instances
            colsample_bytree: Subsample ratio of columns when constructing trees
            min_child_weight: Minimum sum of instance weight needed in a child
            scale_pos_weight: Weight of positive class for imbalanced datasets
            early_stopping_rounds: Stopping rounds for early stopping
            random_state: Random seed for reproducibility
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.min_child_weight = min_child_weight
        self.scale_pos_weight = scale_pos_weight
        self.early_stopping_rounds = early_stopping_rounds
        self.random_state = random_state
        
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            min_child_weight=min_child_weight,
            scale_pos_weight=scale_pos_weight,
            random_state=random_state,
            use_label_encoder=False,
            objective='binary:logistic',
            tree_method='hist'  # For faster training
        )
        
    def fit(
        self,
        X: Union[pd.DataFrame, np.ndarray],
        y: Union[pd.Series, np.ndarray],
        eval_size: float = 0.2,
        **kwargs
    ) -> 'XGBoostModel':
        """
        Fit the XGBoost model to the training data.
        
        Args:
            X: Training features
            y: Target values
            eval_size: Size of evaluation set for early stopping
            **kwargs: Additional arguments to pass to XGBoost's fit method
        
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
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to their importance scores
        """
        if not hasattr(self.model, 'feature_importances_'):
            raise ValueError("Model hasn't been fitted yet")
        
        if isinstance(self.model.feature_importances_, np.ndarray):
            # If we have feature names from training data
            if hasattr(self.model, 'feature_names_in_'):
                return dict(zip(
                    self.model.feature_names_in_,
                    self.model.feature_importances_
                ))
            # If we don't have feature names, use indices
            return {f'feature_{i}': imp for i, imp 
                    in enumerate(self.model.feature_importances_)}
