"""
API routes package.

This package contains all the API route handlers for the credit risk model service.
Each module contains related endpoints grouped by functionality.
"""

from .predict import router as predict_router
from .data_collection import router as data_collection_router
from .device_analytics import router as device_analytics_router
from .comprehensive_data import router as comprehensive_data_router

__all__ = [
    "predict_router",
    "data_collection_router", 
    "device_analytics_router",
    "comprehensive_data_router"
]
