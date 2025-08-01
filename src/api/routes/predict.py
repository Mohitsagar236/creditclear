"""
Prediction API routes with Celery task integration.

This module provides asynchronous prediction endpoints using Celery
for background task processing and MLflow for model serving.
"""

from fastapi import APIRouter, HTTPException, Depends
from celery import Celery
import mlflow
import pandas as pd
import numpy as np
import uuid
from typing import Dict, Any
import os
from pathlib import Path

# Import our schemas
from ..schemas.prediction import PredictionRequest, PredictionResponse
from ...data_processing.feature_engineering import FeatureEngineer

# Create API router
router = APIRouter(prefix="/api/v1", tags=["predictions"])

# Configure Celery app
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

celery_app = Celery(
    "credit_risk_api",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["src.api.routes.predict"]
)

# Configure Celery settings
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_track_started=True,
    task_time_limit=300,  # 5 minutes timeout
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# MLflow configuration
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
MODEL_NAME = os.getenv("MODEL_NAME", "credit_risk_lightgbm")
MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)


@celery_app.task(bind=True, name="run_prediction")
def run_prediction(self, applicant_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Celery task to perform credit risk prediction.
    
    Args:
        applicant_data: Dictionary containing applicant information
        
    Returns:
        Dictionary containing prediction results
    """
    try:
        # Update task status
        self.update_state(
            state="PROCESSING",
            meta={"status": "Loading model and processing data"}
        )
        
        # Load the production model from MLflow
        try:
            model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
            model = mlflow.lightgbm.load_model(model_uri)
        except Exception as e:
            # Fallback to latest version if Production stage doesn't exist
            try:
                model_uri = f"models:/{MODEL_NAME}/latest"
                model = mlflow.lightgbm.load_model(model_uri)
            except Exception as e2:
                raise Exception(f"Failed to load model: {str(e2)}")
        
        # Convert applicant data to DataFrame
        df = pd.DataFrame([applicant_data])
        
        # Feature engineering
        feature_engineer = FeatureEngineer()
        
        # Apply feature engineering if we have the required columns
        try:
            # Check if we can create polynomial features
            if all(col in df.columns for col in feature_engineer.ext_source_cols):
                df = feature_engineer.create_polynomial_features(df)
            
            # Check if we can create credit ratios
            required_cols = ['AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 
                           'DAYS_EMPLOYED', 'DAYS_BIRTH']
            if all(col in df.columns for col in required_cols):
                df = feature_engineer.create_credit_ratios(df)
        except Exception as e:
            # Continue without feature engineering if it fails
            pass
        
        # Handle missing columns that the model expects
        # Get feature names from model if available
        try:
            expected_features = model.feature_name_
            missing_features = set(expected_features) - set(df.columns)
            
            # Add missing features with default values (0)
            for feature in missing_features:
                df[feature] = 0
                
            # Reorder columns to match model expectations
            df = df[expected_features]
        except AttributeError:
            # If model doesn't have feature_name_, proceed with available features
            pass
        
        # Update task status
        self.update_state(
            state="PROCESSING",
            meta={"status": "Running prediction"}
        )
        
        # Make prediction
        prediction_proba = model.predict_proba(df)
        
        # Extract probability of default (class 1)
        if prediction_proba.ndim > 1:
            default_probability = float(prediction_proba[0][1])
        else:
            default_probability = float(prediction_proba[0])
        
        # Determine risk category
        if default_probability <= 0.3:
            risk_category = "low"
        elif default_probability <= 0.7:
            risk_category = "medium"
        else:
            risk_category = "high"
        
        # Calculate confidence score (simplified heuristic)
        confidence_score = float(max(default_probability, 1 - default_probability))
        
        # Prepare result
        result = {
            "prediction_probability": default_probability,
            "risk_category": risk_category,
            "confidence_score": confidence_score,
            "model_version": getattr(model, "_version", "unknown"),
            "features_used": len(df.columns),
            "status": "completed"
        }
        
        return result
        
    except Exception as e:
        # Update task state to failed
        self.update_state(
            state="FAILURE",
            meta={
                "status": "failed",
                "error": str(e),
                "traceback": str(e.__traceback__)
            }
        )
        raise e


@router.post("/predict", response_model=PredictionResponse)
async def predict_credit_risk(request: PredictionRequest) -> PredictionResponse:
    """
    Submit a credit risk prediction request.
    
    Args:
        request: PredictionRequest containing applicant data
        
    Returns:
        PredictionResponse with task ID and status
    """
    try:
        # Convert Pydantic model to dictionary
        applicant_data = request.dict()
        
        # Generate task ID
        task_id = f"pred_{uuid.uuid4()}"
        
        # Submit prediction task to Celery
        task = run_prediction.apply_async(
            args=[applicant_data],
            task_id=task_id
        )
        
        return PredictionResponse(
            task_id=task.id,
            status="pending"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit prediction task: {str(e)}"
        )


@router.get("/predict/{task_id}")
async def get_prediction_result(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a prediction task.
    
    Args:
        task_id: The ID of the prediction task
        
    Returns:
        Dictionary containing task status and result (if completed)
    """
    try:
        # Get task result
        task_result = celery_app.AsyncResult(task_id)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is waiting to be processed"
            }
        elif task_result.state == "PROCESSING":
            response = {
                "task_id": task_id,
                "status": "processing",
                "message": task_result.info.get("status", "Processing...")
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "status": "completed",
                "result": task_result.result
            }
        elif task_result.state == "FAILURE":
            response = {
                "task_id": task_id,
                "status": "failed",
                "error": str(task_result.info.get("error", "Unknown error")),
                "message": "Prediction task failed"
            }
        else:
            response = {
                "task_id": task_id,
                "status": task_result.state.lower(),
                "message": f"Task is in {task_result.state} state"
            }
            
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task result: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for the prediction service.
    
    Returns:
        Dictionary containing health status
    """
    try:
        # Check Celery worker availability
        inspection = celery_app.control.inspect()
        stats = inspection.stats()
        
        if stats:
            celery_status = "healthy"
            worker_count = len(stats)
        else:
            celery_status = "no_workers"
            worker_count = 0
            
        # Check MLflow model availability
        try:
            model_uri = f"models:/{MODEL_NAME}/{MODEL_STAGE}"
            mlflow.lightgbm.load_model(model_uri)
            model_status = "available"
        except Exception:
            try:
                model_uri = f"models:/{MODEL_NAME}/latest"
                mlflow.lightgbm.load_model(model_uri)
                model_status = "available_latest"
            except Exception:
                model_status = "unavailable"
        
        return {
            "status": "healthy",
            "celery_status": celery_status,
            "worker_count": str(worker_count),
            "model_status": model_status,
            "model_name": MODEL_NAME
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/results/{task_id}")
async def get_prediction_result_alias(task_id: str) -> Dict[str, Any]:
    """
    Get the result of a prediction task (alias for /predict/{task_id}).
    
    This endpoint provides the same functionality as /predict/{task_id}
    but with a more intuitive URL structure for the frontend.
    
    Args:
        task_id: The ID of the prediction task
        
    Returns:
        Dictionary containing task status and result (if completed)
    """
    return await get_prediction_result(task_id)
