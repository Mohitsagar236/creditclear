#!/usr/bin/env python3
"""
Simple backend server for CreditClear 2.0.
This is a minimal implementatioif __name__ == "__main__":
    print("🚀 Starting Simple Credit Risk API Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API Documentation: http://localhost:8001/docs")
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)rposes.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Add mock middleware path
mock_middleware_path = project_root / "src" / "utils" / "mock_middleware"
if mock_middleware_path.exists():
    sys.path.insert(0, str(mock_middleware_path))

# Import FastAPI components
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Credit Risk Model API - Simple Version",
    description="Simplified API for credit risk prediction",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Basic routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Credit Risk Model API",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "credit-risk-api"
    }

@app.post("/api/v1/predict")
async def predict_risk(data: dict = None):
    """Mock prediction endpoint."""
    if not data:
        data = {}
    
    # Mock prediction logic
    risk_score = 0.65  # Mock risk score
    
    return {
        "prediction": {
            "risk_score": risk_score,
            "risk_level": "medium" if risk_score > 0.5 else "low",
            "confidence": 0.85,
            "model_version": "2.0.0"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "request_id": "mock-request-123"
    }

@app.get("/metrics")
async def metrics():
    """Endpoint to provide system metrics for monitoring"""
    return {
        "api_version": "1.0.0",
        "active_connections": 1,
        "requests_per_second": 0.5,
        "average_response_time_ms": 120,
        "status": "healthy",
        "total_predictions": 1247,
        "active_users": 89
    }

@app.post("/api/digital-footprint")
async def process_digital_footprint(data: dict = None):
    """Simple endpoint to receive digital footprint data"""
    if not data:
        data = {}
    
    logger.info(f"Received digital footprint data: {data}")
    
    # Basic score calculation
    score = 0.75  # Default score
    insights = [
        "Digital identity verification is strong",
        "Mobile usage patterns show consistent behavior",
        "Payment history indicates reliability"
    ]
    recommendations = [
        "Continue maintaining consistent payment patterns",
        "Consider verifying additional digital accounts"
    ]
    
    # Here we would typically process the data and generate insights
    return {
        "success": True,
        "score": score,
        "insights": insights,
        "recommendations": recommendations
    }

@app.post("/api/comprehensive-prediction")
async def comprehensive_prediction(data: dict = None):
    """Endpoint for comprehensive prediction requests"""
    if not data:
        data = {}
        
    logger.info(f"Received comprehensive prediction request: {data}")
    
    # Mock response
    return {
        "success": True,
        "prediction": 0.82,
        "risk_category": "Low Risk",
        "confidence": 0.9,
        "factors": [
            {"name": "Payment History", "impact": "High", "value": 0.85},
            {"name": "Digital Footprint", "impact": "Medium", "value": 0.75},
            {"name": "Income Stability", "impact": "Medium", "value": 0.8}
        ]
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_status": "operational",
        "models": {
            "lightgbm": "loaded",
            "xgboost": "loaded",
            "ensemble": "ready"
        },
        "database": "connected",
        "cache": "active",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Simple Credit Risk API Server...")
    print("📍 Server will be available at: http://localhost:8001")
    print("📖 API Documentation: http://localhost:8001/docs")
    print()
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)
