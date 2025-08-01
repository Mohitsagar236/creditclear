"""
Device Analytics API Routes - Backend endpoint for receiving React Native device data

This module provides FastAPI routes for collecting and processing device analytics
data from the React Native mobile application in a compliant manner.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
import logging
import json

from src.utils.validators import validate_user_id
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/device-analytics", tags=["device-analytics"])

# Pydantic Models for Device Analytics

class ScreenInfo(BaseModel):
    """Screen and display information"""
    screenWidth: float
    screenHeight: float
    windowWidth: float
    windowHeight: float
    pixelRatio: float
    fontScale: float

class NetworkDetails(BaseModel):
    """Network connection details"""
    isConnectionExpensive: Optional[bool] = None
    ssid: Optional[str] = None
    bssid: Optional[str] = None
    strength: Optional[int] = None
    ipAddress: Optional[str] = None
    subnet: Optional[str] = None

class CellularInfo(BaseModel):
    """Cellular network information"""
    cellularGeneration: Optional[str] = None  # 2g, 3g, 4g, 5g
    carrier: Optional[str] = None

class NetworkData(BaseModel):
    """Complete network information"""
    type: str  # wifi, cellular, bluetooth, ethernet, etc.
    isConnected: bool
    isInternetReachable: Optional[bool] = None
    details: NetworkDetails
    cellularInfo: Optional[CellularInfo] = None

class IOSInfo(BaseModel):
    """iOS-specific device information"""
    deviceCountryCode: Optional[str] = None
    timeZone: Optional[str] = None

class AndroidInfo(BaseModel):
    """Android-specific device information"""
    androidId: Optional[str] = None
    apiLevel: Optional[int] = None
    securityPatch: Optional[str] = None
    codename: Optional[str] = None
    incremental: Optional[str] = None
    installerPackageName: Optional[str] = None

class DeviceInfo(BaseModel):
    """Complete device information"""
    # Device identification (anonymized)
    deviceId: str
    deviceType: str
    
    # Hardware information
    brand: str
    manufacturer: str
    model: str
    deviceName: str
    
    # Operating system
    systemName: str
    systemVersion: str
    buildNumber: str
    
    # App information
    appVersion: str
    buildVersion: str
    bundleId: str
    
    # Hardware capabilities
    isTablet: bool
    hasNotch: Optional[bool] = None
    hasDynamicIsland: Optional[bool] = None
    
    # Security features
    isPinOrFingerprintSet: bool
    supportedAbis: Optional[List[str]] = None
    
    # Memory and storage
    totalMemory: Optional[float] = None
    usedMemory: Optional[float] = None
    totalDiskCapacity: Optional[float] = None
    freeDiskStorage: Optional[float] = None
    
    # Power state
    batteryLevel: Optional[float] = None
    powerState: Optional[Dict[str, Any]] = None
    
    # Security flags
    isEmulator: bool
    
    # Platform info
    platform: str
    platformVersion: str
    
    # Screen information
    screenInfo: ScreenInfo
    
    # Platform-specific info
    iosInfo: Optional[IOSInfo] = None
    androidInfo: Optional[AndroidInfo] = None

class AppData(BaseModel):
    """Application data (compliance-focused)"""
    banking: List[str] = []
    investment: List[str] = []
    lending: List[str] = []
    totalCount: int = 0
    note: Optional[str] = None
    error: Optional[str] = None

class PermissionStatus(BaseModel):
    """Permission status for various device features"""
    location: str = "not_determined"
    camera: str = "not_determined"
    microphone: str = "not_determined"
    storage: str = "not_determined"
    contacts: str = "not_determined"
    notifications: str = "not_determined"
    biometric: str = "not_determined"
    phone: str = "not_determined"
    sms: str = "not_determined"
    error: Optional[str] = None
    note: Optional[str] = None

class RiskFlags(BaseModel):
    """Risk assessment flags derived from device data"""
    isEmulator: bool
    isRooted: bool = False
    isJailbroken: bool = False
    hasSecurityFeatures: bool
    isDebuggingEnabled: bool = False

class DataUsageInfo(BaseModel):
    """Data usage and privacy information"""
    purpose: str
    retention: str
    sharing: str
    userConsent: str

class DeviceProfile(BaseModel):
    """Complete device profile from React Native app"""
    # Metadata
    profileVersion: str
    collectedAt: datetime
    collectionTimeMs: int
    
    # Core data
    device: DeviceInfo
    network: NetworkData
    
    # Compliance data
    apps: AppData
    permissions: PermissionStatus
    
    # Risk assessment
    riskFlags: RiskFlags
    
    # Privacy compliance
    dataUsage: DataUsageInfo
    
    # Optional error information
    error: Optional[str] = None

class DeviceAnalyticsRequest(BaseModel):
    """Request payload for device analytics submission"""
    user_id: str = Field(..., description="User identifier")
    device_profile: DeviceProfile = Field(..., description="Complete device profile")
    collection_timestamp: datetime = Field(..., description="When data was collected")
    app_version: str = Field(..., description="Mobile app version")
    consent_given: bool = Field(True, description="User consent for data collection")
    collection_purpose: str = Field("credit_risk_assessment", description="Purpose of data collection")
    
    @validator('user_id')
    def validate_user_id_format(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('User ID cannot be empty')
        return v.strip()
    
    @validator('consent_given')
    def validate_consent(cls, v):
        if not v:
            raise ValueError('User consent is required for data collection')
        return v

class DeviceAnalyticsResponse(BaseModel):
    """Response for device analytics submission"""
    success: bool
    message: str
    analytics_id: Optional[str] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None  # low, medium, high
    recommendations: Optional[List[str]] = None
    processed_at: datetime

# Risk Assessment Functions

def calculate_risk_score(device_profile: DeviceProfile) -> Dict[str, Any]:
    """
    Calculate risk score based on device characteristics
    Returns risk score (0-100) and risk level
    """
    risk_score = 0.0
    risk_factors = []
    
    # Emulator detection (high risk)
    if device_profile.riskFlags.isEmulator:
        risk_score += 40
        risk_factors.append("Device is an emulator")
    
    # Rooting/Jailbreaking detection (high risk)
    if device_profile.riskFlags.isRooted or device_profile.riskFlags.isJailbroken:
        risk_score += 35
        risk_factors.append("Device is rooted/jailbroken")
    
    # Security features (negative risk - good)
    if not device_profile.riskFlags.hasSecurityFeatures:
        risk_score += 15
        risk_factors.append("No security features enabled")
    
    # Debugging enabled (medium risk)
    if device_profile.riskFlags.isDebuggingEnabled:
        risk_score += 20
        risk_factors.append("Developer debugging enabled")
    
    # Old OS version (low-medium risk)
    try:
        system_version = device_profile.device.systemVersion
        if device_profile.device.platform.lower() == 'android':
            # Check Android version
            if int(system_version.split('.')[0]) < 10:
                risk_score += 10
                risk_factors.append("Outdated Android version")
        elif device_profile.device.platform.lower() == 'ios':
            # Check iOS version
            if float(system_version.split('.')[0]) < 14:
                risk_score += 10
                risk_factors.append("Outdated iOS version")
    except (ValueError, IndexError):
        pass
    
    # Device age estimation (based on model patterns)
    device_model = device_profile.device.model.lower()
    if any(old_indicator in device_model for old_indicator in ['mini', '5s', '6', 'se']):
        risk_score += 5
        risk_factors.append("Older device model")
    
    # Network risk factors
    if device_profile.network.details.isConnectionExpensive:
        # Users on expensive connections might be more cost-conscious
        risk_score -= 5  # Slight positive indicator
    
    # Cap risk score at 100
    risk_score = min(risk_score, 100.0)
    
    # Determine risk level
    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_factors": risk_factors
    }

def generate_recommendations(device_profile: DeviceProfile, risk_assessment: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on device profile and risk assessment"""
    recommendations = []
    
    if risk_assessment["risk_level"] == "high":
        recommendations.extend([
            "Consider additional identity verification steps",
            "Implement enhanced fraud monitoring",
            "Request additional documentation"
        ])
    
    if device_profile.riskFlags.isEmulator:
        recommendations.append("Block application from emulated devices")
    
    if device_profile.riskFlags.isRooted or device_profile.riskFlags.isJailbroken:
        recommendations.append("Require additional security verification for rooted devices")
    
    if not device_profile.riskFlags.hasSecurityFeatures:
        recommendations.append("Encourage user to enable device security features")
    
    if device_profile.network.type == "cellular":
        recommendations.append("Optimize data usage for cellular connections")
    
    return recommendations

# API Routes

@router.post("/submit", response_model=DeviceAnalyticsResponse)
async def submit_device_analytics(
    request: DeviceAnalyticsRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit device analytics data from React Native app
    
    This endpoint receives device analytics data collected by the mobile app
    and processes it for credit risk assessment and fraud prevention.
    """
    try:
        logger.info(f"Receiving device analytics for user: {request.user_id}")
        
        # Validate timestamp (should be recent)
        time_diff = datetime.utcnow() - request.collection_timestamp
        if time_diff > timedelta(hours=1):
            logger.warning(f"Old analytics data received: {time_diff}")
        
        # Calculate risk assessment
        risk_assessment = calculate_risk_score(request.device_profile)
        
        # Generate recommendations
        recommendations = generate_recommendations(
            request.device_profile, 
            risk_assessment
        )
        
        # Generate analytics ID
        analytics_id = f"DA_{request.user_id}_{int(datetime.utcnow().timestamp())}"
        
        # Log important security flags
        if request.device_profile.riskFlags.isEmulator:
            logger.warning(f"Emulator detected for user {request.user_id}")
        
        if request.device_profile.riskFlags.isRooted or request.device_profile.riskFlags.isJailbroken:
            logger.warning(f"Rooted/Jailbroken device detected for user {request.user_id}")
        
        # Store analytics data (background task)
        background_tasks.add_task(
            store_device_analytics,
            analytics_id,
            request.user_id,
            request.device_profile,
            risk_assessment
        )
        
        # Prepare response
        response = DeviceAnalyticsResponse(
            success=True,
            message="Device analytics processed successfully",
            analytics_id=analytics_id,
            risk_score=risk_assessment["risk_score"],
            risk_level=risk_assessment["risk_level"],
            recommendations=recommendations,
            processed_at=datetime.utcnow()
        )
        
        logger.info(f"Device analytics processed for user {request.user_id}: risk_level={risk_assessment['risk_level']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing device analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process device analytics: {str(e)}"
        )

@router.get("/risk-profile/{user_id}")
async def get_user_risk_profile(user_id: str):
    """
    Get the latest risk profile for a user based on device analytics
    """
    try:
        # This would typically query a database
        # For now, return a placeholder response
        
        logger.info(f"Retrieving risk profile for user: {user_id}")
        
        # In a real implementation, you would:
        # 1. Query database for latest analytics
        # 2. Calculate current risk score
        # 3. Return comprehensive risk profile
        
        return {
            "user_id": user_id,
            "risk_score": 25.0,
            "risk_level": "low",
            "last_updated": datetime.utcnow(),
            "device_count": 1,
            "emulator_detected": False,
            "rooted_device": False,
            "security_features": True
        }
        
    except Exception as e:
        logger.error(f"Error retrieving risk profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve risk profile: {str(e)}"
        )

@router.get("/analytics/{analytics_id}")
async def get_analytics_details(analytics_id: str):
    """
    Get detailed analytics information by analytics ID
    """
    try:
        logger.info(f"Retrieving analytics details: {analytics_id}")
        
        # In a real implementation, query database for analytics details
        return {
            "analytics_id": analytics_id,
            "processed_at": datetime.utcnow(),
            "status": "processed",
            "risk_assessment": {
                "risk_score": 15.0,
                "risk_level": "low",
                "factors": []
            }
        }
        
    except Exception as e:
        logger.error(f"Error retrieving analytics details: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=f"Analytics not found: {analytics_id}"
        )

# Background Tasks

async def store_device_analytics(
    analytics_id: str,
    user_id: str,
    device_profile: DeviceProfile,
    risk_assessment: Dict[str, Any]
):
    """
    Store device analytics data in database (background task)
    """
    try:
        logger.info(f"Storing device analytics: {analytics_id}")
        
        # In a real implementation, you would:
        # 1. Insert into analytics database table
        # 2. Update user risk profile
        # 3. Trigger fraud detection rules
        # 4. Send alerts if high risk detected
        
        # Example database storage (pseudo-code):
        # await db.device_analytics.insert({
        #     "analytics_id": analytics_id,
        #     "user_id": user_id,
        #     "device_profile": device_profile.dict(),
        #     "risk_assessment": risk_assessment,
        #     "created_at": datetime.utcnow()
        # })
        
        logger.info(f"Device analytics stored successfully: {analytics_id}")
        
    except Exception as e:
        logger.error(f"Error storing device analytics: {str(e)}")
        # Don't raise exception in background task
        # Log error and continue

# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for device analytics service"""
    return {
        "status": "healthy",
        "service": "device-analytics",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
