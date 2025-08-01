"""
Pydantic schemas for device data collection API.

This module defines the request and response models for device data endpoints,
including validation and serialization for mobile device information, network data,
and coarse location data.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class PlatformType(str, Enum):
    """Device platform enumeration."""
    ANDROID = "android"
    IOS = "ios"


class NetworkType(str, Enum):
    """Network connectivity type enumeration."""
    WIFI = "wifi"
    CELLULAR = "cellular"
    NONE = "none"
    UNKNOWN = "unknown"


class DeviceInfo(BaseModel):
    """Device hardware and software information."""
    device_id: str = Field(..., description="Anonymized device identifier")
    device_type: str = Field(..., description="Device type (Smartphone, Tablet)")
    brand: str = Field(..., description="Device brand")
    manufacturer: str = Field(..., description="Device manufacturer")
    model: str = Field(..., description="Device model")
    device_name: str = Field(..., description="Device name")
    
    # Operating system information
    system_name: str = Field(..., description="Operating system name")
    system_version: str = Field(..., description="OS version")
    build_number: Optional[str] = Field(None, description="OS build number")
    
    # App information
    app_version: str = Field(..., description="App version")
    build_version: str = Field(..., description="App build version")
    bundle_id: str = Field(..., description="App bundle identifier")
    
    # Hardware capabilities
    is_tablet: bool = Field(default=False, description="Whether device is a tablet")
    has_notch: Optional[bool] = Field(None, description="Whether device has a notch")
    has_dynamic_island: Optional[bool] = Field(None, description="Whether device has dynamic island")
    
    # Security features
    is_pin_or_fingerprint_set: bool = Field(..., description="Whether PIN or biometric auth is set")
    supported_abis: Optional[List[str]] = Field(None, description="Supported ABIs")
    
    # Memory and storage
    total_memory: Optional[int] = Field(None, description="Total device memory in bytes")
    used_memory: Optional[int] = Field(None, description="Used memory in bytes")
    total_disk_capacity: Optional[int] = Field(None, description="Total disk capacity in bytes")
    free_disk_storage: Optional[int] = Field(None, description="Free disk storage in bytes")
    
    # Power state
    battery_level: Optional[float] = Field(None, description="Battery level (0.0-1.0)")
    
    # Security flags
    is_emulator: bool = Field(default=False, description="Whether device is an emulator")
    platform: PlatformType = Field(..., description="Device platform")
    platform_version: str = Field(..., description="Platform version")
    
    @validator('battery_level')
    def validate_battery_level(cls, v):
        """Validate battery level is between 0 and 1."""
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError("Battery level must be between 0.0 and 1.0")
        return v


class ScreenInfo(BaseModel):
    """Screen information."""
    screen_width: int = Field(..., description="Screen width in pixels")
    screen_height: int = Field(..., description="Screen height in pixels")
    window_width: int = Field(..., description="Window width in pixels")
    window_height: int = Field(..., description="Window height in pixels")
    pixel_ratio: float = Field(..., description="Device pixel ratio")
    font_scale: float = Field(..., description="Font scale factor")
    
    @validator('pixel_ratio', 'font_scale')
    def validate_positive(cls, v):
        """Validate positive values."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v


class NetworkInfo(BaseModel):
    """Network connectivity information."""
    type: NetworkType = Field(..., description="Network connection type")
    is_connected: bool = Field(..., description="Whether device is connected to internet")
    is_wifi_enabled: bool = Field(default=False, description="Whether WiFi is enabled")
    is_cellular_enabled: bool = Field(default=False, description="Whether cellular is enabled")
    
    # Network details (optional)
    wifi_ssid: Optional[str] = Field(None, description="WiFi SSID (if connected)")
    cellular_generation: Optional[str] = Field(None, description="Cellular generation (3G, 4G, 5G)")
    is_connection_expensive: Optional[bool] = Field(None, description="Whether connection is expensive")
    
    @validator('wifi_ssid')
    def validate_wifi_ssid(cls, v):
        """Validate WiFi SSID is not too long."""
        if v and len(v) > 32:  # Standard WiFi SSID max length
            raise ValueError("WiFi SSID too long")
        return v


class CoarseLocationInfo(BaseModel):
    """Coarse location information (compliant with privacy requirements)."""
    latitude: float = Field(..., description="Coarse latitude (rounded to ~1km precision)")
    longitude: float = Field(..., description="Coarse longitude (rounded to ~1km precision)")
    accuracy: float = Field(..., description="Location accuracy in meters (minimum 1000m)")
    timestamp: datetime = Field(..., description="Location timestamp")
    source: str = Field(default="geolocation_service", description="Location source")
    
    @validator('accuracy')
    def validate_accuracy(cls, v):
        """Validate minimum accuracy for coarse location."""
        if v < 1000:  # Minimum 1km accuracy for compliance
            raise ValueError("Location accuracy must be at least 1000 meters for compliance")
        return v
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """Validate latitude range."""
        if v < -90 or v > 90:
            raise ValueError("Latitude must be between -90 and 90")
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """Validate longitude range."""
        if v < -180 or v > 180:
            raise ValueError("Longitude must be between -180 and 180")
        return v


class AppInfo(BaseModel):
    """Application information (compliance-focused)."""
    total_count: int = Field(0, description="Total number of installed apps")
    has_banking_apps: bool = Field(default=False, description="Whether banking apps are detected")
    has_payment_apps: bool = Field(default=False, description="Whether payment apps are detected")
    has_financial_apps: bool = Field(default=False, description="Whether financial apps are detected")
    
    # Note: No app list scanning to comply with Google Play policies
    compliance_note: str = Field(
        default="No app list scanning - compliance with privacy policies",
        description="Compliance information"
    )


class RiskFlags(BaseModel):
    """Device risk assessment flags."""
    is_emulator: bool = Field(default=False, description="Device is an emulator")
    is_rooted_or_jailbroken: bool = Field(default=False, description="Device is rooted/jailbroken")
    has_debugging_enabled: bool = Field(default=False, description="Developer debugging enabled")
    has_security_features: bool = Field(default=True, description="Has basic security features")
    is_os_outdated: bool = Field(default=False, description="Operating system is outdated")


class MobileDeviceData(BaseModel):
    """Complete mobile device data payload."""
    user_id: str = Field(..., description="Unique user identifier")
    collection_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data collection timestamp")
    
    # Core device information
    device_info: DeviceInfo = Field(..., description="Device hardware and software information")
    screen_info: ScreenInfo = Field(..., description="Screen configuration")
    network_info: NetworkInfo = Field(..., description="Network connectivity information")
    
    # Optional compliance-focused data
    coarse_location: Optional[CoarseLocationInfo] = Field(None, description="Coarse location (if permission granted)")
    app_info: Optional[AppInfo] = Field(None, description="Application information (compliance-focused)")
    risk_flags: Optional[RiskFlags] = Field(None, description="Security risk assessment flags")
    
    # Additional metadata
    profile_version: str = Field(default="1.0.0", description="Device profile version")
    collection_time_ms: Optional[int] = Field(None, description="Time taken to collect data in milliseconds")
    
    @validator('collection_timestamp')
    def validate_timestamp_recent(cls, v):
        """Validate timestamp is recent (within last hour)."""
        now = datetime.utcnow()
        time_diff = now - v
        if time_diff.total_seconds() > 3600:  # 1 hour
            raise ValueError("Collection timestamp is too old")
        return v
    
    @validator('collection_time_ms')
    def validate_collection_time(cls, v):
        """Validate collection time is reasonable."""
        if v is not None and (v < 0 or v > 60000):  # Max 60 seconds
            raise ValueError("Collection time must be between 0 and 60000 milliseconds")
        return v


class MobileDeviceDataRequest(BaseModel):
    """Request model for mobile device data upload."""
    device_data: MobileDeviceData = Field(..., description="Mobile device data payload")


class MobileDeviceDataResponse(BaseModel):
    """Response model for mobile device data upload."""
    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Response message")
    user_id: str = Field(..., description="User ID from the request")
    records_processed: int = Field(..., description="Number of records processed")
    risk_assessment: Optional[Dict[str, Any]] = Field(None, description="Risk assessment results")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class DeviceDataError(BaseModel):
    """Error response model for device data endpoints."""
    success: bool = Field(False, description="Request was unsuccessful")
    error_code: str = Field(..., description="Error code")
    error_message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


# Legacy compatibility models (for existing endpoint)
class DeviceDataSubmission(BaseModel):
    """Legacy request model for device data submission (backward compatibility)."""
    user_id: str = Field(..., description="Unique identifier for the user")
    device_data: Dict[str, Any] = Field(..., description="Device data payload")


class DeviceDataResponse(BaseModel):
    """Legacy response model for device data submission (backward compatibility)."""
    success: bool
    records_processed: int
    message: str


# Add alias for backward compatibility
DeviceDataRequest = MobileDeviceDataRequest
