#!/usr/bin/env python3
"""
Simple startup script for the Credit Risk API server without complex dependencies.
"""

import sys
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
from datetime import datetime
import logging

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Credit Risk Model API",
    description="Simple API for credit risk prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", 
                  "http://localhost:5173", 
                  "http://localhost:8080",
                  "http://localhost:8082",
                  "https://creditclear.vercel.app",
                  "https://creditclear-git-master-mohitsagar236.vercel.app",
                  "https://creditclear-mohitsagar236.vercel.app",
                  "*"],  # Include Vercel domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Simple request/response models
class PredictionRequest(BaseModel):
    """Simple prediction request model."""
    applicant_data: Dict[str, Any]
    device_data: Optional[Dict[str, Any]] = None
    alternative_data: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    """Simple prediction response model."""
    risk_score: float
    risk_level: str
    confidence: float
    timestamp: str

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Welcome to the Credit Risk Model API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
        "health_check": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "credit-risk-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict_risk(request: PredictionRequest) -> PredictionResponse:
    """
    Simple credit risk prediction endpoint.
    """
    try:
        # Simple mock prediction logic
        # In a real implementation, this would load and use ML models
        
        # Extract some basic features for demo
        income = request.applicant_data.get('income', 50000)
        credit_amount = request.applicant_data.get('credit_amount', 25000)
        age = request.applicant_data.get('age', 35)
        
        # Simple risk calculation
        income_ratio = credit_amount / max(income, 1)
        age_factor = 1.0 if age >= 25 else 0.8
        
        # Basic risk score (0-1)
        risk_score = min(0.9, max(0.1, income_ratio * 0.7 / age_factor))
        
        # Determine risk level
        if risk_score < 0.3:
            risk_level = "Low"
        elif risk_score < 0.6:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        # Mock confidence
        confidence = 0.85
        
        return PredictionResponse(
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

class ComprehensivePredictionRequest(BaseModel):
    type: str
    data: Dict[str, Any]

@app.post("/api/comprehensive-prediction")
async def comprehensive_prediction(request: ComprehensivePredictionRequest):
    """
    Endpoint to receive comprehensive data from the frontend.
    """
    try:
        # Log the received data
        logger.info(f"Received comprehensive data of type: {request.type}")
        
        # Simple mock analysis based on received data
        score = 0.75 # Base score
        if request.data and 'digitalIdentity' in request.data:
            if request.data['digitalIdentity'].get('emailVerified'):
                score += 0.05
            if request.data['digitalIdentity'].get('phoneVerified'):
                score += 0.05
        
        if request.data and 'deviceTechnical' in request.data:
            score += (request.data['deviceTechnical']['security'].get('score', 0.85) - 0.85) * 0.2

        if request.data and 'utilityServices' in request.data:
            score += (request.data['utilityServices'].get('paymentConsistency', 0.85) - 0.85) * 0.2
            
        score = max(0, min(1, score)) # Clamp score

        return {
            "success": True,
            "score": score,
            "insights": [
                "Comprehensive data processed successfully.",
                "Digital identity appears consistent.",
                "Device security metrics are within acceptable range."
            ],
            "recommendations": [
                "Continue to maintain a secure digital presence.",
                "Ensure timely utility payments."
            ]
        }
    except Exception as e:
        logger.error(f"Comprehensive prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Comprehensive prediction failed: {str(e)}")


@app.get("/api/v1/models")
async def list_models() -> Dict[str, Any]:
    """List available models."""
    return {
        "models": [
            {
                "name": "simple_risk_model",
                "version": "1.0.0",
                "type": "classification",
                "status": "active"
            }
        ],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
def get_metrics():
    """
    Sample metrics endpoint.
    """
    return {
        "status": "success",
        "data": {
            "metric1": 100,
            "metric2": 200
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Credit Risk API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
