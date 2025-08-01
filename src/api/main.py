"""
Main FastAPI application entry point.

This module creates and configures the FastAPI application for the
credit risk model API service with enhanced middleware and monitoring.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from typing import Dict
import logging
from datetime import datetime

# Import route modules
from src.api.routes import predict, data_collection, device_analytics, comprehensive_data, digital_footprint, ai_alternative_data

# Import enhanced middleware
from src.api.middleware import (
    APILoggingMiddleware,
    RateLimitMiddleware, 
    CacheMiddleware,
    PerformanceMonitoringMiddleware,
    SecurityMiddleware
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app instance with enhanced configuration
app = FastAPI(
    title="Credit Risk Model API",
    description="Advanced API for credit risk prediction with alternative data collection, real-time monitoring, and comprehensive analytics",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "predictions", "description": "Credit risk prediction endpoints"},
        {"name": "data-collection", "description": "Alternative data collection endpoints"},
        {"name": "device-analytics", "description": "Device and behavioral analytics"},
        {"name": "AI Alternative Data", "description": "AI-powered alternative data credit risk assessment"},
        {"name": "monitoring", "description": "System monitoring and health checks"},
        {"name": "admin", "description": "Administrative endpoints"}
    ]
)

# Configure CORS with enhanced settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time", "X-Cache", "X-RateLimit-Remaining-Minute"]
)

# Add enhanced middleware stack (order matters!)
app.add_middleware(SecurityMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(CacheMiddleware, cache_ttl=300)  # 5 minutes cache
app.add_middleware(RateLimitMiddleware, calls_per_minute=100, calls_per_hour=5000)
app.add_middleware(APILoggingMiddleware)

# Store performance monitor reference for metrics endpoint
performance_monitor = None
for middleware in app.user_middleware:
    if isinstance(middleware.cls, type) and issubclass(middleware.cls, PerformanceMonitoringMiddleware):
        performance_monitor = middleware

# Include routers with enhanced error handling
try:
    app.include_router(predict.router, prefix="/api/v1", tags=["predictions"])
    app.include_router(data_collection.router, prefix="/api/v1", tags=["data-collection"])
    app.include_router(device_analytics.router, prefix="/api/v1", tags=["device-analytics"])
    app.include_router(comprehensive_data.router, prefix="/api/v1", tags=["data-collection"])
    app.include_router(digital_footprint.router, prefix="/api", tags=["digital-footprint"])
    app.include_router(ai_alternative_data.router, prefix="/api/v1", tags=["AI Alternative Data"])
    logger.info("All routers successfully included")
except Exception as e:
    logger.error(f"Failed to include some routers: {e}")

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"Unhandled exception for request {request_id}: {str(exc)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            "url": str(request.url),
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.get("/", tags=["monitoring"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with enhanced system information.
    
    Returns:
        Dict containing welcome message and comprehensive API information
    """
    return {
        "message": "Welcome to the Advanced Credit Risk Model API",
        "version": "3.0.0",
        "status": "running",
        "features": [
            "Real-time credit risk prediction",
            "AI-powered alternative data analysis",
            "Automatic device analytics collection", 
            "Behavioral pattern recognition",
            "Digital footprint assessment",
            "Comprehensive risk scoring",
            "Performance monitoring",
            "Rate limiting and caching",
            "Comprehensive logging"
        ],
        "documentation": "/docs",
        "health_check": "/health",
        "metrics": "/metrics",
        "admin": "/admin/dashboard",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["monitoring"])
async def health_check() -> Dict[str, str]:
    """
    Enhanced health check endpoint with system status.
    
    Returns:
        Dict containing detailed health status
    """
    return {
        "status": "healthy",
        "service": "credit-risk-api",
        "version": "3.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "available",
        "database": "connected",  # TODO: Add actual DB health check
        "cache": "available",     # TODO: Add actual Redis health check
        "ml_models": "loaded"     # TODO: Add actual model health check
    }


@app.get("/metrics", tags=["monitoring"])
async def get_metrics() -> Dict:
    """
    Performance metrics endpoint.
    
    Returns:
        Current system performance metrics
    """
    # Get metrics from performance monitor if available
    if performance_monitor and hasattr(performance_monitor, 'kwargs'):
        monitor_instance = performance_monitor.kwargs.get('instance')
        if monitor_instance:
            return {
                "metrics": monitor_instance.get_metrics(),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return {
        "message": "Metrics collection in progress",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/admin/dashboard", tags=["admin"])
async def admin_dashboard() -> Dict:
    """
    Administrative dashboard endpoint.
    
    Returns:
        System administration information
    """
    return {
        "system": {
            "api_version": "3.0.0",
            "python_version": "3.9+",
            "status": "operational"
        },
        "endpoints": {
            "predictions": "/api/v1/predict",
            "data_collection": "/api/v1/collect-data", 
            "device_analytics": "/api/v1/device-analytics",
            "comprehensive_data": "/api/v1/comprehensive-data",
            "ai_alternative_data": "/api/v1/ai-alternative-data"
        },
        "monitoring": {
            "health": "/health",
            "metrics": "/metrics",
            "logs": "structured_logging_enabled"
        },
        "security": {
            "rate_limiting": "enabled",
            "cors": "configured",
            "security_headers": "enabled"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Run the app with uvicorn if script is executed directly
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
