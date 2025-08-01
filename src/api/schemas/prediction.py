"""
Pydantic schemas for credit risk prediction API.

This module defines the request and response models for the prediction endpoints,
including validation and serialization for credit risk assessment data.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Literal
from enum import Enum


class EducationType(str, Enum):
    """Education type enumeration."""
    LOWER_SECONDARY = "Lower secondary"
    SECONDARY = "Secondary / secondary special"
    INCOMPLETE_HIGHER = "Incomplete higher"
    HIGHER_EDUCATION = "Higher education"
    ACADEMIC_DEGREE = "Academic degree"


class ContractType(str, Enum):
    """Contract type enumeration."""
    CASH_LOANS = "Cash loans"
    REVOLVING_LOANS = "Revolving loans"


class CodeGender(str, Enum):
    """Gender code enumeration."""
    MALE = "M"
    FEMALE = "F"
    XNA = "XNA"


class PredictionRequest(BaseModel):
    """
    Request schema for credit risk prediction.
    
    Contains the most important features from the Home Credit dataset
    required for making credit risk predictions.
    """
    
    # Financial Information
    AMT_INCOME_TOTAL: float = Field(
        ..., 
        gt=0, 
        description="Income of the client",
        example=202500.0
    )
    
    AMT_CREDIT: float = Field(
        ..., 
        gt=0, 
        description="Credit amount of the loan",
        example=406597.5
    )
    
    AMT_ANNUITY: Optional[float] = Field(
        None, 
        gt=0, 
        description="Loan annuity",
        example=24700.5
    )
    
    AMT_GOODS_PRICE: Optional[float] = Field(
        None, 
        ge=0, 
        description="For consumer loans it is the price of the goods for which the loan is given",
        example=351000.0
    )
    
    # Personal Information
    NAME_CONTRACT_TYPE: ContractType = Field(
        ..., 
        description="Identification if loan is cash or revolving",
        example="Cash loans"
    )
    
    CODE_GENDER: CodeGender = Field(
        ..., 
        description="Gender of the client",
        example="M"
    )
    
    FLAG_OWN_CAR: Literal["Y", "N"] = Field(
        ..., 
        description="Flag if client owns a car",
        example="N"
    )
    
    FLAG_OWN_REALTY: Literal["Y", "N"] = Field(
        ..., 
        description="Flag if client owns a house or flat",
        example="Y"
    )
    
    CNT_CHILDREN: int = Field(
        ..., 
        ge=0, 
        description="Number of children the client has",
        example=0
    )
    
    # Education and Employment
    NAME_EDUCATION_TYPE: EducationType = Field(
        ..., 
        description="Level of highest education the client achieved",
        example="Higher education"
    )
    
    DAYS_BIRTH: int = Field(
        ..., 
        lt=0, 
        description="Client's age in days (negative value)",
        example=-9461
    )
    
    DAYS_EMPLOYED: int = Field(
        ..., 
        description="How many days before the application the person started current employment (negative value)",
        example=-637
    )
    
    # External Sources (Credit Bureau Information)
    EXT_SOURCE_1: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Normalized score from external data source",
        example=0.083037
    )
    
    EXT_SOURCE_2: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Normalized score from external data source",
        example=0.262949
    )
    
    EXT_SOURCE_3: Optional[float] = Field(
        None, 
        ge=0, 
        le=1, 
        description="Normalized score from external data source",
        example=0.139376
    )
    
    # Additional Important Features
    REGION_POPULATION_RELATIVE: Optional[float] = Field(
        None, 
        ge=0, 
        description="Normalized population of region where client lives",
        example=0.018801
    )
    
    HOUR_APPR_PROCESS_START: Optional[int] = Field(
        None, 
        ge=0, 
        le=23, 
        description="Approximately at what hour did the client apply for the loan",
        example=10
    )
    
    @validator('DAYS_BIRTH')
    def validate_age(cls, v):
        """Validate that age is reasonable (18-100 years)."""
        age_days = abs(v)
        age_years = age_days / 365.25
        if not (18 <= age_years <= 100):
            raise ValueError('Age must be between 18 and 100 years')
        return v
    
    @validator('DAYS_EMPLOYED')
    def validate_employment(cls, v):
        """Validate employment days."""
        if v > 0:
            raise ValueError('DAYS_EMPLOYED should be negative or zero')
        # Check for unrealistic employment duration (more than 60 years)
        if abs(v) > 365.25 * 60:
            raise ValueError('Employment duration seems unrealistic')
        return v
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "AMT_INCOME_TOTAL": 202500.0,
                "AMT_CREDIT": 406597.5,
                "AMT_ANNUITY": 24700.5,
                "AMT_GOODS_PRICE": 351000.0,
                "NAME_CONTRACT_TYPE": "Cash loans",
                "CODE_GENDER": "M",
                "FLAG_OWN_CAR": "N",
                "FLAG_OWN_REALTY": "Y",
                "CNT_CHILDREN": 0,
                "NAME_EDUCATION_TYPE": "Higher education",
                "DAYS_BIRTH": -9461,
                "DAYS_EMPLOYED": -637,
                "EXT_SOURCE_1": 0.083037,
                "EXT_SOURCE_2": 0.262949,
                "EXT_SOURCE_3": 0.139376,
                "REGION_POPULATION_RELATIVE": 0.018801,
                "HOUR_APPR_PROCESS_START": 10
            }
        }


class PredictionResponse(BaseModel):
    """
    Response schema for credit risk prediction.
    
    Contains the prediction task information and status.
    """
    
    task_id: str = Field(
        ..., 
        description="Unique identifier for the prediction task",
        example="pred_123e4567-e89b-12d3-a456-426614174000"
    )
    
    status: Literal["pending", "processing", "completed", "failed"] = Field(
        ..., 
        description="Current status of the prediction task",
        example="pending"
    )
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "task_id": "pred_123e4567-e89b-12d3-a456-426614174000",
                "status": "pending"
            }
        }


class PredictionResult(BaseModel):
    """
    Schema for the actual prediction result.
    
    Contains the credit risk prediction and associated metadata.
    """
    
    prediction_probability: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Probability of default (0 = low risk, 1 = high risk)",
        example=0.127
    )
    
    risk_category: Literal["low", "medium", "high"] = Field(
        ..., 
        description="Risk category based on prediction probability",
        example="low"
    )
    
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Model confidence in the prediction",
        example=0.85
    )
    
    model_version: str = Field(
        ..., 
        description="Version of the model used for prediction",
        example="v1.0.0"
    )
    
    features_used: int = Field(
        ..., 
        description="Number of features used in the prediction",
        example=15
    )
    
    @validator('risk_category')
    def determine_risk_category(cls, v, values):
        """Automatically determine risk category based on probability."""
        if 'prediction_probability' in values:
            prob = values['prediction_probability']
            if prob <= 0.3:
                return "low"
            elif prob <= 0.7:
                return "medium"
            else:
                return "high"
        return v
    
    class Config:
        """Pydantic model configuration."""
        schema_extra = {
            "example": {
                "prediction_probability": 0.127,
                "risk_category": "low",
                "confidence_score": 0.85,
                "model_version": "v1.0.0",
                "features_used": 15
            }
        }
