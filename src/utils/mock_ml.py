"""
Mock implementations for ML libraries when not available.
This allows the system to run without installing heavy ML packages.
"""

import warnings
import numpy as np
from typing import Any, Dict, Optional


class MockLightGBMRegressor:
    """Mock LightGBM regressor for when package is not available."""
    
    def __init__(self, **kwargs):
        self.params = kwargs
        self.is_fitted = False
        
    def fit(self, X, y, **kwargs):
        """Mock fit method."""
        self.is_fitted = True
        return self
        
    def predict(self, X, **kwargs):
        """Mock predict method - returns random probabilities."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Return mock probabilities between 0.1 and 0.9
        n_samples = len(X) if hasattr(X, '__len__') else 1
        return np.random.uniform(0.1, 0.9, n_samples)
        
    def predict_proba(self, X, **kwargs):
        """Mock predict_proba method."""
        predictions = self.predict(X, **kwargs)
        # Return 2-class probabilities
        return np.column_stack([1 - predictions, predictions])


class MockXGBRegressor:
    """Mock XGBoost regressor for when package is not available."""
    
    def __init__(self, **kwargs):
        self.params = kwargs
        self.is_fitted = False
        
    def fit(self, X, y, **kwargs):
        """Mock fit method."""
        self.is_fitted = True
        return self
        
    def predict(self, X, **kwargs):
        """Mock predict method - returns random probabilities."""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
            
        n_samples = len(X) if hasattr(X, '__len__') else 1
        return np.random.uniform(0.1, 0.9, n_samples)
        
    def predict_proba(self, X, **kwargs):
        """Mock predict_proba method."""
        predictions = self.predict(X, **kwargs)
        return np.column_stack([1 - predictions, predictions])


class MockJoblib:
    """Mock joblib module for when package is not available."""
    
    @staticmethod
    def load(filename):
        """Mock load method - returns a mock model."""
        warnings.warn(f"Mock joblib.load called for {filename}. Returning mock model.")
        return MockLightGBMRegressor()
        
    @staticmethod
    def dump(obj, filename, **kwargs):
        """Mock dump method."""
        warnings.warn(f"Mock joblib.dump called for {filename}.")
        return [filename]


class MockSklearnPreprocessing:
    """Mock sklearn preprocessing module."""
    
    class StandardScaler:
        def __init__(self):
            self.is_fitted = False
            
        def fit(self, X):
            self.is_fitted = True
            return self
            
        def transform(self, X):
            if not self.is_fitted:
                raise ValueError("Scaler must be fitted before transform")
            return np.array(X)  # Return unchanged
            
        def fit_transform(self, X):
            return self.fit(X).transform(X)
    
    class PolynomialFeatures:
        def __init__(self, degree=2, **kwargs):
            self.degree = degree
            self.is_fitted = False
            
        def fit(self, X):
            self.is_fitted = True
            return self
            
        def transform(self, X):
            if not self.is_fitted:
                raise ValueError("PolynomialFeatures must be fitted before transform")
            X = np.array(X)
            # Simple mock: just add squared features
            if X.ndim == 1:
                X = X.reshape(1, -1)
            squared = X ** 2
            return np.hstack([X, squared])
            
        def fit_transform(self, X):
            return self.fit(X).transform(X)


class MockSklearnEnsemble:
    """Mock sklearn ensemble module."""
    
    class VotingRegressor:
        def __init__(self, estimators, **kwargs):
            self.estimators = estimators
            self.is_fitted = False
            
        def fit(self, X, y, **kwargs):
            self.is_fitted = True
            return self
            
        def predict(self, X, **kwargs):
            if not self.is_fitted:
                raise ValueError("Ensemble must be fitted before prediction")
            n_samples = len(X) if hasattr(X, '__len__') else 1
            return np.random.uniform(0.1, 0.9, n_samples)


def get_mock_lightgbm():
    """Get mock lightgbm module."""
    class MockLightGBM:
        LGBMRegressor = MockLightGBMRegressor
    return MockLightGBM()


def get_mock_xgboost():
    """Get mock xgboost module."""
    class MockXGBoost:
        XGBRegressor = MockXGBRegressor
    return MockXGBoost()


def get_mock_sklearn():
    """Get mock sklearn modules."""
    class MockSklearn:
        preprocessing = MockSklearnPreprocessing()
        ensemble = MockSklearnEnsemble()
    return MockSklearn()


# Export mock joblib
mock_joblib = MockJoblib()
