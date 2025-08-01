"""
Ensemble model implementation for credit risk prediction.

This module implements various ensemble methods combining multiple models
for improved credit risk prediction accuracy and robustness.
"""

import warnings
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Union, Optional
import logging

try:
    from sklearn.ensemble import VotingClassifier, StackingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    warnings.warn("Scikit-learn not available. Using mock implementation.")
    from ..utils.mock_ml import get_mock_sklearn
    sklearn_mock = get_mock_sklearn()
    VotingClassifier = sklearn_mock.ensemble.VotingRegressor
    StackingClassifier = sklearn_mock.ensemble.VotingRegressor
    
    class LogisticRegression:
        def __init__(self, **kwargs):
            self.is_fitted = False
        def fit(self, X, y):
            self.is_fitted = True
            return self
        def predict(self, X):
            return np.random.uniform(0, 1, len(X))
    
    def cross_val_score(estimator, X, y, **kwargs):
        return np.random.uniform(0.7, 0.9, 5)  # Mock CV scores
    
    SKLEARN_AVAILABLE = False

from .base_model import BaseModel
from .lightgbm_model import LightGBMModel
from .xgboost_model import XGBoostModel

logger = logging.getLogger(__name__)


class EnsembleModel(BaseModel):
    """
    Ensemble model for credit risk prediction.
    
    This class implements ensemble methods that combine multiple base models
    to create a more robust and accurate predictor.
    """
    
    def __init__(
        self,
        ensemble_type: str = "voting",
        voting_type: str = "soft",
        models: Optional[List[BaseModel]] = None,
        weights: Optional[List[float]] = None,
        meta_learner: Optional[Any] = None,
        random_state: int = 42
    ):
        """
        Initialize the ensemble model.
        
        Args:
            ensemble_type: Type of ensemble ("voting" or "stacking")
            voting_type: Voting strategy for VotingClassifier ("hard" or "soft")
            models: List of base models to ensemble
            weights: Weights for each model in voting ensemble
            meta_learner: Meta-learner for stacking ensemble
            random_state: Random seed for reproducibility
        """
        super().__init__("ensemble_model", random_state)
        
        self.ensemble_type = ensemble_type
        self.voting_type = voting_type
        self.weights = weights
        self.meta_learner = meta_learner or LogisticRegression(random_state=random_state)
        
        # Initialize default models if none provided
        if models is None:
            self.base_models = [
                LightGBMModel(random_state=random_state),
                XGBoostModel(random_state=random_state)
            ]
        else:
            self.base_models = models
            
        self.model_names = [model.model_name for model in self.base_models]
        
    def _create_ensemble(self) -> Union[VotingClassifier, StackingClassifier]:
        """
        Create the ensemble classifier based on the specified type.
        
        Returns:
            Configured ensemble classifier
        """
        # Prepare estimators list
        estimators = [(model.model_name, model.model) for model in self.base_models]
        
        if self.ensemble_type == "voting":
            return VotingClassifier(
                estimators=estimators,
                voting=self.voting_type,
                weights=self.weights
            )
        elif self.ensemble_type == "stacking":
            return StackingClassifier(
                estimators=estimators,
                final_estimator=self.meta_learner,
                cv=5,
                stack_method="predict_proba" if hasattr(self.meta_learner, "predict_proba") else "predict"
            )
        else:
            raise ValueError(f"Unsupported ensemble type: {self.ensemble_type}")
    
    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> 'EnsembleModel':
        """
        Train the ensemble model.
        
        Args:
            X: Training features
            y: Training targets
            
        Returns:
            Self for method chaining
        """
        logger.info(f"Training ensemble model with {len(self.base_models)} base models")
        
        # Store feature names
        if isinstance(X, pd.DataFrame):
            self.feature_names = list(X.columns)
        
        # Train each base model
        for i, model in enumerate(self.base_models):
            logger.info(f"Training base model {i+1}/{len(self.base_models)}: {model.model_name}")
            model.fit(X, y)
        
        # Create and train ensemble
        self.model = self._create_ensemble()
        self.model.fit(X, y)
        
        self.is_fitted = True
        logger.info("Ensemble model training completed")
        
        return self
    
    def predict(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Make predictions using the ensemble model.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        X = self.validate_input(X)
        return self.model.predict(X)
    
    def predict_proba(self, X: Union[pd.DataFrame, np.ndarray]) -> np.ndarray:
        """
        Predict class probabilities using the ensemble model.
        
        Args:
            X: Features to predict on
            
        Returns:
            Array of prediction probabilities
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        X = self.validate_input(X)
        return self.model.predict_proba(X)
    
    def get_individual_predictions(self, X: Union[pd.DataFrame, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Get predictions from each individual base model.
        
        Args:
            X: Features to predict on
            
        Returns:
            Dictionary mapping model names to their predictions
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before making predictions")
            
        X = self.validate_input(X)
        predictions = {}
        
        for model in self.base_models:
            predictions[model.model_name] = model.predict_proba(X)
            
        return predictions
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get averaged feature importance scores from base models.
        
        Returns:
            Dictionary mapping feature names to averaged importance scores
        """
        if not self.is_fitted:
            return None
            
        importances = {}
        valid_models = 0
        
        for model in self.base_models:
            model_importance = model.get_feature_importance()
            if model_importance is not None:
                valid_models += 1
                for feature, importance in model_importance.items():
                    if feature in importances:
                        importances[feature] += importance
                    else:
                        importances[feature] = importance
        
        if valid_models > 0:
            # Average the importances
            for feature in importances:
                importances[feature] /= valid_models
                
            return importances
        
        return None
    
    def get_model_weights(self) -> Optional[Dict[str, float]]:
        """
        Get the weights assigned to each base model.
        
        Returns:
            Dictionary mapping model names to their weights
        """
        if self.ensemble_type == "voting" and self.weights is not None:
            return dict(zip(self.model_names, self.weights))
        elif self.ensemble_type == "stacking" and hasattr(self.model, 'final_estimator_'):
            # For stacking, weights are learned by the meta-learner
            if hasattr(self.model.final_estimator_, 'coef_'):
                weights = self.model.final_estimator_.coef_[0]
                return dict(zip(self.model_names, weights))
        
        return None
    
    def evaluate_individual_models(self, X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> Dict[str, float]:
        """
        Evaluate each individual base model using cross-validation.
        
        Args:
            X: Validation features
            y: Validation targets
            
        Returns:
            Dictionary mapping model names to their CV scores
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before evaluation")
            
        scores = {}
        for model in self.base_models:
            try:
                cv_scores = cross_val_score(model.model, X, y, cv=5, scoring='roc_auc')
                scores[model.model_name] = cv_scores.mean()
            except Exception as e:
                logger.warning(f"Could not evaluate model {model.model_name}: {e}")
                scores[model.model_name] = 0.0
                
        return scores
    
    def get_ensemble_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the ensemble model.
        
        Returns:
            Dictionary containing ensemble model information
        """
        base_info = self.get_model_info()
        ensemble_info = {
            'ensemble_type': self.ensemble_type,
            'voting_type': self.voting_type if self.ensemble_type == "voting" else None,
            'base_models': self.model_names,
            'model_count': len(self.base_models),
            'weights': self.get_model_weights(),
            'meta_learner': str(self.meta_learner) if self.ensemble_type == "stacking" else None
        }
        
        return {**base_info, **ensemble_info}
