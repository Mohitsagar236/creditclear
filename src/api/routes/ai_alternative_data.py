"""
AI Alternative Data Credit Risk API

This module provides API endpoints for comprehensive credit risk assessment
using AI models that process traditional Kaggle data along with alternative
data sources including device analytics and behavioral patterns.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging
import asyncio
import numpy as np
import pandas as pd

from ..services.auth import get_current_user
from ..schemas.prediction import PredictionRequest, PredictionResponse
from ...models.ai_alternative_data_model import AIAlternativeDataModel
from ...utils.data_loader import load_kaggle_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-alternative-data", tags=["AI Alternative Data"])

# Global model instance (to be loaded on startup)
ai_model = None


class AlternativeDataRequest(BaseModel):
    """Request model for alternative data credit risk assessment."""
    
    # Traditional application data (Kaggle format)
    applicant_data: Dict[str, Any] = Field(
        ..., 
        description="Traditional application data in Kaggle Home Credit format"
    )
    
    # Device analytics data
    device_data: Dict[str, Any] = Field(
        ...,
        description="Device analytics data including hardware, OS, network info"
    )
    
    # Alternative data sources
    location_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Location and mobility data"
    )
    
    utility_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Utility payment and subscription data"
    )
    
    digital_footprint: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Digital footprint and online behavior data"
    )
    
    communication_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Communication patterns and contact data"
    )
    
    # Request metadata
    request_id: Optional[str] = Field(
        default=None,
        description="Optional request ID for tracking"
    )
    
    include_explanations: bool = Field(
        default=True,
        description="Whether to include detailed explanations and insights"
    )


class AIRiskAssessmentResponse(BaseModel):
    """Response model for AI alternative data risk assessment."""
    
    # Core prediction results
    risk_score: float = Field(
        ...,
        description="Overall risk score (0-1, where 1 is highest risk)",
        ge=0.0,
        le=1.0
    )
    
    risk_level: str = Field(
        ...,
        description="Risk level category: Low, Medium, High"
    )
    
    confidence: float = Field(
        ...,
        description="Model confidence in the prediction (0-1)",
        ge=0.0,
        le=1.0
    )
    
    # Detailed model outputs
    model_scores: Dict[str, float] = Field(
        ...,
        description="Individual scores from different model components"
    )
    
    # Insights and explanations
    insights: List[str] = Field(
        ...,
        description="Human-readable insights about the risk factors"
    )
    
    recommendations: List[str] = Field(
        ...,
        description="Actionable recommendations based on the assessment"
    )
    
    # Feature analysis
    feature_contributions: Dict[str, float] = Field(
        ...,
        description="Top feature contributions to the prediction"
    )
    
    data_source_weights: Dict[str, float] = Field(
        ...,
        description="Weights assigned to different data sources"
    )
    
    # Alternative data analysis
    device_risk_factors: List[str] = Field(
        default=[],
        description="Specific device-related risk factors identified"
    )
    
    behavioral_risk_factors: List[str] = Field(
        default=[],
        description="Behavioral pattern risk factors identified"
    )
    
    # Metadata
    assessment_timestamp: str = Field(
        ...,
        description="Timestamp of the assessment"
    )
    
    model_version: str = Field(
        default="AI-v1.0",
        description="Version of the AI model used"
    )
    
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Time taken to process the request in milliseconds"
    )


class BatchAssessmentRequest(BaseModel):
    """Request model for batch alternative data assessments."""
    
    assessments: List[AlternativeDataRequest] = Field(
        ...,
        description="List of assessment requests to process"
    )
    
    batch_id: Optional[str] = Field(
        default=None,
        description="Optional batch ID for tracking"
    )


class BatchAssessmentResponse(BaseModel):
    """Response model for batch assessments."""
    
    batch_id: str = Field(
        ...,
        description="Batch processing ID"
    )
    
    total_requests: int = Field(
        ...,
        description="Total number of requests in the batch"
    )
    
    successful_assessments: int = Field(
        ...,
        description="Number of successfully processed assessments"
    )
    
    failed_assessments: int = Field(
        ...,
        description="Number of failed assessments"
    )
    
    results: List[Union[AIRiskAssessmentResponse, Dict[str, str]]] = Field(
        ...,
        description="List of assessment results or error information"
    )
    
    batch_processing_time_ms: float = Field(
        ...,
        description="Total time taken to process the batch"
    )


@router.on_event("startup")
async def load_ai_model():
    """Load the AI alternative data model on startup."""
    global ai_model
    try:
        logger.info("Loading AI Alternative Data Model...")
        ai_model = AIAlternativeDataModel()
        
        # Load training data and train the model
        kaggle_data = load_kaggle_data()
        if kaggle_data is not None and 'TARGET' in kaggle_data.columns:
            # Sample data for faster training in demo
            sample_size = min(10000, len(kaggle_data))
            sample_data = kaggle_data.sample(n=sample_size, random_state=42)
            
            # Simulate alternative data for training
            device_features = ai_model.extract_device_features({
                'device': {'model': 'iPhone 13', 'platform': 'iOS', 'systemVersion': '16.0', 'isPinOrFingerprintSet': True},
                'network': {'type': 'wifi', 'isInternetReachable': True},
                'riskFlags': {'isEmulator': False, 'isRooted': False},
                'apps': {'totalCount': 5, 'banking': [], 'investment': [], 'lending': []}
            })
            
            behavioral_features = ai_model.extract_behavioral_features({
                'location': {'homeLocation': 'detected', 'travelPatterns': 'regular_commuter'},
                'utility': {'mobileRecharge': 'regular', 'electricityBill': 'consistent'},
                'digitalFootprint': {},
                'communication': {}
            })
            
            # Prepare features
            X_kaggle = ai_model.preprocess_kaggle_data(sample_data.drop('TARGET', axis=1))
            X_combined = ai_model.combine_features(X_kaggle, device_features, behavioral_features)
            y = sample_data['TARGET']
            
            # Train the model
            ai_model.fit(X_combined, y)
            logger.info("AI Alternative Data Model loaded and trained successfully!")
        else:
            logger.warning("Could not load Kaggle data for training")
            
    except Exception as e:
        logger.error(f"Failed to load AI model: {e}")
        ai_model = None


@router.post("/assess", response_model=AIRiskAssessmentResponse)
async def assess_credit_risk(
    request: AlternativeDataRequest,
    current_user: Dict = Depends(get_current_user)
) -> AIRiskAssessmentResponse:
    """
    Perform comprehensive credit risk assessment using AI and alternative data.
    
    This endpoint combines traditional credit data with device analytics,
    behavioral patterns, and digital footprint data to provide a comprehensive
    risk assessment using advanced AI models.
    """
    start_time = datetime.now()
    
    if ai_model is None or not ai_model.is_fitted:
        raise HTTPException(
            status_code=503,
            detail="AI Alternative Data Model is not available"
        )
    
    try:
        # Prepare data structures
        kaggle_df = pd.DataFrame([request.applicant_data])
        
        # Combine alternative data
        alternative_data = {
            'location': request.location_data or {},
            'utility': request.utility_data or {},
            'digitalFootprint': request.digital_footprint or {},
            'communication': request.communication_data or {}
        }
        
        # Perform comprehensive risk assessment
        assessment_result = ai_model.predict_comprehensive_risk(
            kaggle_data=kaggle_df,
            device_data=request.device_data,
            alternative_data=alternative_data
        )
        
        # Analyze risk factors
        device_risk_factors = _analyze_device_risks(request.device_data)
        behavioral_risk_factors = _analyze_behavioral_risks(alternative_data)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Prepare response
        response = AIRiskAssessmentResponse(
            risk_score=assessment_result['risk_score'],
            risk_level=assessment_result['risk_level'],
            confidence=assessment_result['confidence'],
            model_scores=assessment_result['model_scores'],
            insights=assessment_result['insights'],
            recommendations=assessment_result['recommendations'],
            feature_contributions=assessment_result['feature_contributions'],
            data_source_weights=assessment_result['data_source_weights'],
            device_risk_factors=device_risk_factors,
            behavioral_risk_factors=behavioral_risk_factors,
            assessment_timestamp=assessment_result['assessment_timestamp'],
            processing_time_ms=processing_time
        )
        
        logger.info(f"AI assessment completed for user {current_user.get('username', 'unknown')} "
                   f"in {processing_time:.2f}ms - Risk: {assessment_result['risk_level']}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in AI credit risk assessment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process credit risk assessment: {str(e)}"
        )


@router.post("/batch-assess", response_model=BatchAssessmentResponse)
async def batch_assess_credit_risk(
    request: BatchAssessmentRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> BatchAssessmentResponse:
    """
    Perform batch credit risk assessment for multiple applicants.
    
    This endpoint allows processing multiple credit risk assessments
    efficiently in a single request.
    """
    start_time = datetime.now()
    
    if ai_model is None or not ai_model.is_fitted:
        raise HTTPException(
            status_code=503,
            detail="AI Alternative Data Model is not available"
        )
    
    batch_id = request.batch_id or f"batch_{int(datetime.now().timestamp())}"
    results = []
    successful_count = 0
    failed_count = 0
    
    try:
        for i, assessment_request in enumerate(request.assessments):
            try:
                # Process individual assessment
                kaggle_df = pd.DataFrame([assessment_request.applicant_data])
                alternative_data = {
                    'location': assessment_request.location_data or {},
                    'utility': assessment_request.utility_data or {},
                    'digitalFootprint': assessment_request.digital_footprint or {},
                    'communication': assessment_request.communication_data or {}
                }
                
                assessment_result = ai_model.predict_comprehensive_risk(
                    kaggle_data=kaggle_df,
                    device_data=assessment_request.device_data,
                    alternative_data=alternative_data
                )
                
                # Analyze risk factors
                device_risk_factors = _analyze_device_risks(assessment_request.device_data)
                behavioral_risk_factors = _analyze_behavioral_risks(alternative_data)
                
                result = AIRiskAssessmentResponse(
                    risk_score=assessment_result['risk_score'],
                    risk_level=assessment_result['risk_level'],
                    confidence=assessment_result['confidence'],
                    model_scores=assessment_result['model_scores'],
                    insights=assessment_result['insights'],
                    recommendations=assessment_result['recommendations'],
                    feature_contributions=assessment_result['feature_contributions'],
                    data_source_weights=assessment_result['data_source_weights'],
                    device_risk_factors=device_risk_factors,
                    behavioral_risk_factors=behavioral_risk_factors,
                    assessment_timestamp=assessment_result['assessment_timestamp']
                )
                
                results.append(result)
                successful_count += 1
                
            except Exception as e:
                logger.error(f"Failed to process assessment {i}: {e}")
                results.append({
                    "error": str(e),
                    "assessment_index": i,
                    "request_id": assessment_request.request_id or f"req_{i}"
                })
                failed_count += 1
        
        # Calculate total processing time
        total_processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        response = BatchAssessmentResponse(
            batch_id=batch_id,
            total_requests=len(request.assessments),
            successful_assessments=successful_count,
            failed_assessments=failed_count,
            results=results,
            batch_processing_time_ms=total_processing_time
        )
        
        logger.info(f"Batch assessment completed: {successful_count} successful, "
                   f"{failed_count} failed in {total_processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in batch credit risk assessment: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch assessment: {str(e)}"
        )


@router.get("/model-info")
async def get_ai_model_info(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get information about the AI Alternative Data Model."""
    if ai_model is None:
        raise HTTPException(
            status_code=503,
            detail="AI Alternative Data Model is not available"
        )
    
    return ai_model.get_model_info()


@router.get("/feature-importance")
async def get_feature_importance(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, float]:
    """Get feature importance scores from the AI model."""
    if ai_model is None or not ai_model.is_fitted:
        raise HTTPException(
            status_code=503,
            detail="AI Alternative Data Model is not available or not trained"
        )
    
    return ai_model.feature_importance_scores


@router.post("/simulate-assessment")
async def simulate_assessment(
    current_user: Dict = Depends(get_current_user)
) -> AIRiskAssessmentResponse:
    """
    Simulate a comprehensive AI assessment with mock data.
    
    This endpoint is useful for testing and demonstration purposes.
    """
    if ai_model is None:
        raise HTTPException(
            status_code=503,
            detail="AI Alternative Data Model is not available"
        )
    
    # Create mock data for simulation
    mock_kaggle_data = {
        'AMT_INCOME_TOTAL': 180000,
        'AMT_CREDIT': 450000,
        'AMT_ANNUITY': 18500,
        'DAYS_BIRTH': -12000,
        'DAYS_EMPLOYED': -1800,
        'CNT_FAM_MEMBERS': 2,
        'NAME_CONTRACT_TYPE': 'Cash loans',
        'CODE_GENDER': 'F',
        'FLAG_OWN_CAR': 'N',
        'FLAG_OWN_REALTY': 'Y',
        'NAME_INCOME_TYPE': 'Working',
        'NAME_EDUCATION_TYPE': 'Higher education',
        'NAME_FAMILY_STATUS': 'Married',
        'NAME_HOUSING_TYPE': 'House / apartment'
    }
    
    mock_device_data = {
        'device': {
            'model': 'iPhone 14',
            'platform': 'iOS',
            'systemVersion': '16.4',
            'isPinOrFingerprintSet': True,
            'totalMemory': 6442450944,  # 6GB
            'totalDiskCapacity': 128849018880,  # 128GB
            'isTablet': False
        },
        'network': {
            'type': 'wifi',
            'isConnected': True,
            'isInternetReachable': True,
            'details': {
                'isConnectionExpensive': False
            }
        },
        'riskFlags': {
            'isEmulator': False,
            'isRooted': False,
            'isJailbroken': False,
            'hasSecurityFeatures': True,
            'isDebuggingEnabled': False
        },
        'apps': {
            'totalCount': 8,
            'banking': ['SBI', 'ICICI'],
            'investment': ['Zerodha'],
            'lending': []
        }
    }
    
    mock_alternative_data = {
        'location': {
            'currentCity': 'Mumbai',
            'homeLocation': 'detected',
            'workLocation': 'detected',
            'travelPatterns': 'regular_commuter'
        },
        'utility': {
            'mobileRecharge': 'regular',
            'electricityBill': 'consistent',
            'internetUsage': 'high',
            'subscriptionServices': 'multiple'
        },
        'digitalFootprint': {
            'socialMediaPresence': 'active',
            'onlineActivity': 'regular'
        },
        'communication': {
            'contactStability': 'high',
            'communicationFrequency': 'regular'
        }
    }
    
    # Create request object
    request = AlternativeDataRequest(
        applicant_data=mock_kaggle_data,
        device_data=mock_device_data,
        location_data=mock_alternative_data['location'],
        utility_data=mock_alternative_data['utility'],
        digital_footprint=mock_alternative_data['digitalFootprint'],
        communication_data=mock_alternative_data['communication'],
        request_id="simulation_001"
    )
    
    # Process the assessment
    return await assess_credit_risk(request, current_user)


def _analyze_device_risks(device_data: Dict[str, Any]) -> List[str]:
    """Analyze device data for specific risk factors."""
    risk_factors = []
    
    risk_flags = device_data.get('riskFlags', {})
    device_info = device_data.get('device', {})
    
    if risk_flags.get('isEmulator'):
        risk_factors.append("Device emulation detected")
    
    if risk_flags.get('isRooted') or risk_flags.get('isJailbroken'):
        risk_factors.append("Device is rooted/jailbroken")
    
    if not risk_flags.get('hasSecurityFeatures'):
        risk_factors.append("No device security features enabled")
    
    if risk_flags.get('isDebuggingEnabled'):
        risk_factors.append("Developer debugging is enabled")
    
    # Check OS version
    platform = device_info.get('platform', '').lower()
    version = device_info.get('systemVersion', '')
    
    if platform == 'android' and version:
        try:
            major_version = int(version.split('.')[0])
            if major_version < 10:
                risk_factors.append("Outdated Android version")
        except (ValueError, IndexError):
            pass
    elif platform == 'ios' and version:
        try:
            major_version = int(version.split('.')[0])
            if major_version < 14:
                risk_factors.append("Outdated iOS version")
        except (ValueError, IndexError):
            pass
    
    return risk_factors


def _analyze_behavioral_risks(alternative_data: Dict[str, Any]) -> List[str]:
    """Analyze behavioral data for specific risk factors."""
    risk_factors = []
    
    location_data = alternative_data.get('location', {})
    utility_data = alternative_data.get('utility', {})
    
    # Location risks
    if location_data.get('homeLocation') != 'detected':
        risk_factors.append("Home location not consistently detected")
    
    travel_pattern = location_data.get('travelPatterns', '').lower()
    if 'nomadic' in travel_pattern or 'frequent_travel' in travel_pattern:
        risk_factors.append("Irregular travel patterns")
    
    # Utility payment risks
    if utility_data.get('electricityBill', '').lower() not in ['consistent', 'regular']:
        risk_factors.append("Irregular utility payment patterns")
    
    if utility_data.get('mobileRecharge', '').lower() not in ['consistent', 'regular']:
        risk_factors.append("Irregular mobile recharge patterns")
    
    return risk_factors
