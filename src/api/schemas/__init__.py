"""
API schemas package for request/response models.
"""

from .prediction import *
from .device_data import *

__all__ = [
    # Prediction schemas
    "PredictionRequest",
    "PredictionResponse", 
    # Device data schemas
    "MobileDeviceData",
    "MobileDeviceDataRequest",
    "MobileDeviceDataResponse",
    "DeviceInfo",
    "NetworkInfo",
    "CoarseLocationInfo",
    "AppInfo",
    "RiskFlags",
    "ScreenInfo",
    "DeviceDataError",
    # Legacy schemas
    "DeviceDataSubmission",
    "DeviceDataResponse",
    "DeviceDataRequest",  # Alias for MobileDeviceDataRequest
]
