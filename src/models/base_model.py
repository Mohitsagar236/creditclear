"""
Base model class for credit risk models.

This module provides the abstract base class for all credit risk models,
defining the common interface and functionality.
"""

import warnings
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
import pickle
from pathlib import Path
import logging

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    warnings.warn("Joblib not available. Using mock implementation.")
    from ..utils.mock_ml import mock_joblib as joblib
    JOBLIB_AVAILABLE = False

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for credit risk models.
    
    This class defines the common interface that all credit risk models
    must implement, including training, prediction, and model persistence.
    """
    
    def __init__(self, model_name: str, random_state: int = 42):
        """
        Initialize the base model.
        
        Args:
            model_name: Name of the model
            random_state: Random seed for reproducibility
        """
        self.model_name = model_name
        self.random_state = random_state
        self.model = None
        self.is_fitted = False
        self.feature_names = None
        self.target_column = 'TARGET'
        
    @abstractmethod
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> 'BaseModel':
        """
        Train the model on the given data.
        
        Args:
            X: Training features
            y: Training targets
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Make predictions on the given data.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of predictions
        """
        pass
    
    @abstractmethod
    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Predict class probabilities for the given data.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of prediction probabilities
        """
        pass
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance scores.
        
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if not self.is_fitted or self.model is None:
            return None
            
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            if self.feature_names is not None:
                return dict(zip(self.feature_names, importances))
            else:
                return dict(zip([f'feature_{i}' for i in range(len(importances))], importances))
        
        return None
    
    def save_model(self, filepath: Union[str, Path]) -> None:
        """
        Save the trained model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise ValueError("Cannot save model that hasn't been fitted yet")
            
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'model': self.model,
            'model_name': self.model_name,
            'feature_names': self.feature_names,
            'is_fitted': self.is_fitted,
            'random_state': self.random_state
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: Union[str, Path]) -> 'BaseModel':
        """
        Load a trained model from disk.
        
        Args:
            filepath: Path to load the model from
            
        Returns:
            Self for method chaining
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Model file not found: {filepath}")
            
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.model_name = model_data['model_name']
        self.feature_names = model_data['feature_names']
        self.is_fitted = model_data['is_fitted']
        self.random_state = model_data['random_state']
        
        logger.info(f"Model loaded from {filepath}")
        return self
    
    def validate_input(self, X: Union[pd.DataFrame, np.ndarray]) -> Union[pd.DataFrame, np.ndarray]:
        """
        Validate input data format and features.
        
        Args:
            X: Input data to validate
            
        Returns:
            Validated input data
            
        Raises:
            ValueError: If input validation fails
        """
        if isinstance(X, pd.DataFrame):
            if self.feature_names is not None:
                missing_features = set(self.feature_names) - set(X.columns)
                if missing_features:
                    raise ValueError(f"Missing required features: {missing_features}")
                    
                # Reorder columns to match training order
                X = X[self.feature_names]
                
        elif isinstance(X, np.ndarray):
            if self.feature_names is not None and X.shape[1] != len(self.feature_names):
                raise ValueError(f"Expected {len(self.feature_names)} features, got {X.shape[1]}")
        else:
            raise ValueError("Input must be pandas DataFrame or numpy array")
            
        return X
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary containing model information
        """
        return {
            'model_name': self.model_name,
            'is_fitted': self.is_fitted,
            'feature_count': len(self.feature_names) if self.feature_names else None,
            'feature_names': self.feature_names,
            'random_state': self.random_state,
            'model_type': self.__class__.__name__
        }
