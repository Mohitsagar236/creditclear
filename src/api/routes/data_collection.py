"""
Data collection routes for the credit risk assessment API.

This module provides FastAPI routes for initiating data collection flows,
including Account Aggregator consent management and device data submission.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from uuid import uuid4

from src.data_processing.collectors import (
    AccountAggregatorCollector,
    DeviceDataCollector,
    ConsentStatus,
    DataSourceType
)
from src.api.schemas.device_data import (
    MobileDeviceDataRequest,
    MobileDeviceDataResponse,
    DeviceDataError,
    # Legacy schemas for backward compatibility
    DeviceDataSubmission,
    DeviceDataResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/data-collection", tags=["Data Collection"])

# Initialize collectors (these would typically be dependency injected)
aa_collector = AccountAggregatorCollector()
device_collector = DeviceDataCollector()

# Pydantic models for request/response schemas
class AAConsentRequest(BaseModel):
    """Request model for Account Aggregator consent initiation."""
    user_id: str = Field(..., description="Unique identifier for the user")
    customer_mobile: str = Field(..., description="Customer's mobile number")
    customer_name: Optional[str] = Field(None, description="Customer's name")
    fi_types: List[str] = Field(
        default=["DEPOSIT", "TERM_DEPOSIT", "RECURRING_DEPOSIT"],
        description="List of Financial Information types to request"
    )
    purpose: str = Field(
        default="Credit Assessment",
        description="Purpose for data collection"
    )
    duration_days: int = Field(
        default=30,
        description="Number of days the consent should be valid",
        ge=1,
        le=365
    )
    
    @validator('customer_mobile')
    def validate_mobile(cls, v):
        """Validate mobile number format."""
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Mobile number must be 10 digits")
        return v
    
    @validator('fi_types')
    def validate_fi_types(cls, v):
        """Validate FI types."""
        valid_types = [
            "DEPOSIT", "TERM_DEPOSIT", "RECURRING_DEPOSIT", 
            "CREDIT_CARD", "MUTUAL_FUND", "INSURANCE"
        ]
        for fi_type in v:
            if fi_type not in valid_types:
                raise ValueError(f"Invalid FI type: {fi_type}")
        return v


class AAConsentResponse(BaseModel):
    """Response model for Account Aggregator consent initiation."""
    success: bool
    consent_handle: str
    consent_id: Optional[str]
    consent_url: Optional[str]
    status: str
    message: str
    expires_at: datetime


class ConsentStatusRequest(BaseModel):
    """Request model for checking consent status."""
    consent_handle: str = Field(..., description="Consent handle to check")


class ConsentStatusResponse(BaseModel):
    """Response model for consent status."""
    consent_handle: str
    status: str
    message: str


class FIDataRequest(BaseModel):
    """Request model for FI data collection."""
    consent_handle: str = Field(..., description="Consent handle for data collection")


class FIDataResponse(BaseModel):
    """Response model for FI data request."""
    success: bool
    session_id: Optional[str]
    consent_id: Optional[str]
    message: str


# Dependency for getting configured AA collector
async def get_aa_collector() -> AccountAggregatorCollector:
    """Get configured Account Aggregator collector."""
    if not aa_collector._is_configured:
        # Configure with default/environment settings
        config = {
            "api_base_url": "https://fiu-uat.setu.co",
            "client_id": "test_client_id",  # Should come from environment
            "client_secret": "test_client_secret",  # Should come from environment
            "webhook_url": "https://your-domain.com/webhook/aa-consent"
        }
        if not aa_collector.configure(config):
            raise HTTPException(
                status_code=500,
                detail="Account Aggregator service not available"
            )
    return aa_collector


# Dependency for getting configured device collector
async def get_device_collector() -> DeviceDataCollector:
    """Get configured device data collector."""
    if not device_collector._is_configured:
        config = {
            "validation_rules": {},
            "privacy_settings": {"anonymize_location": True}
        }
        device_collector.configure(config)
    return device_collector


@router.post("/initiate-aa-flow", response_model=AAConsentResponse)
async def initiate_aa_flow(
    request: AAConsentRequest,
    aa_collector: AccountAggregatorCollector = Depends(get_aa_collector)
):
    """
    Initiate Account Aggregator consent flow for financial data collection.
    
    This endpoint creates a consent request with the Setu AA API and returns
    the consent URL that should be presented to the user for approval.
    
    Args:
        request: AA consent request details
        aa_collector: Configured Account Aggregator collector
        
    Returns:
        Consent details including URL for user approval
        
    Raises:
        HTTPException: If consent creation fails
    """
    try:
        logger.info(f"Initiating AA flow for user {request.user_id}")
        
        # Create consent request
        consent = aa_collector.create_consent_request(
            user_id=request.user_id,
            fi_types=request.fi_types,
            purpose=request.purpose,
            duration_days=request.duration_days,
            customer_mobile=request.customer_mobile,
            customer_name=request.customer_name
        )
        
        if consent.status == ConsentStatus.DENIED:
            raise HTTPException(
                status_code=400,
                detail="Failed to create consent request"
            )
        
        response = AAConsentResponse(
            success=True,
            consent_handle=consent.consent_handle,
            consent_id=consent.consent_id,
            consent_url=consent.consent_url,
            status=consent.status.value,
            message="Consent request created successfully. Please redirect user to consent_url.",
            expires_at=consent.expires_at
        )
        
        logger.info(f"AA consent created: {consent.consent_handle}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate AA flow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/consent-status", response_model=ConsentStatusResponse)
async def get_consent_status(
    consent_handle: str,
    aa_collector: AccountAggregatorCollector = Depends(get_aa_collector)
):
    """
    Check the status of an Account Aggregator consent request.
    
    Args:
        consent_handle: Consent handle to check
        aa_collector: Configured Account Aggregator collector
        
    Returns:
        Current consent status
        
    Raises:
        HTTPException: If consent handle is invalid
    """
    try:
        logger.info(f"Checking consent status: {consent_handle}")
        
        status = aa_collector.get_consent_status(consent_handle)
        
        status_messages = {
            ConsentStatus.PENDING: "Consent is pending user approval",
            ConsentStatus.GRANTED: "Consent has been granted by user",
            ConsentStatus.DENIED: "Consent was denied or is invalid",
            ConsentStatus.EXPIRED: "Consent has expired",
            ConsentStatus.REVOKED: "Consent has been revoked by user"
        }
        
        response = ConsentStatusResponse(
            consent_handle=consent_handle,
            status=status.value,
            message=status_messages.get(status, "Unknown status")
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get consent status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/request-fi-data", response_model=FIDataResponse)
async def request_fi_data(
    request: FIDataRequest,
    aa_collector: AccountAggregatorCollector = Depends(get_aa_collector)
):
    """
    Request FI data collection using a granted consent.
    
    This endpoint initiates the actual data fetching process after
    the user has granted consent.
    
    Args:
        request: FI data request details
        aa_collector: Configured Account Aggregator collector
        
    Returns:
        Session details for data collection
        
    Raises:
        HTTPException: If consent is not granted or request fails
    """
    try:
        logger.info(f"Requesting FI data for consent: {request.consent_handle}")
        
        # Check consent status first
        status = aa_collector.get_consent_status(request.consent_handle)
        if status != ConsentStatus.GRANTED:
            raise HTTPException(
                status_code=400,
                detail=f"Consent not granted. Current status: {status.value}"
            )
        
        # Request FI data
        result = aa_collector.request_fi_data(request.consent_handle)
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to request FI data")
            )
        
        response = FIDataResponse(
            success=True,
            session_id=result.get("session_id"),
            consent_id=result.get("consent_id"),
            message="FI data request initiated successfully. Use session_id to fetch data."
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request FI data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/fetch-fi-data/{session_id}")
async def fetch_fi_data(
    session_id: str,
    aa_collector: AccountAggregatorCollector = Depends(get_aa_collector)
):
    """
    Fetch FI data using a session ID.
    
    Args:
        session_id: Session ID from FI data request
        aa_collector: Configured Account Aggregator collector
        
    Returns:
        Financial data in JSON format
        
    Raises:
        HTTPException: If data fetching fails
    """
    try:
        logger.info(f"Fetching FI data for session: {session_id}")
        
        result = aa_collector.fetch_fi_data(session_id)
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.error_message or "Failed to fetch FI data"
            )
        
        # Convert DataFrame to dict for JSON response
        data_dict = result.data.to_dict("records") if result.data is not None else []
        
        return JSONResponse(content={
            "success": True,
            "data": data_dict,
            "metadata": result.metadata,
            "records_count": result.records_collected,
            "collection_timestamp": result.collection_timestamp.isoformat()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch FI data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/submit-device-data", response_model=DeviceDataResponse)
async def submit_device_data(
    request: DeviceDataSubmission,
    device_collector: DeviceDataCollector = Depends(get_device_collector)
):
    """
    Submit device data for processing and feature extraction.
    
    Args:
        request: Device data submission
        device_collector: Configured device data collector
        
    Returns:
        Processing results
        
    Raises:
        HTTPException: If data processing fails
    """
    try:
        logger.info(f"Processing device data for user {request.user_id}")
        
        result = device_collector.process_device_data(request.device_data)
        
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.error_message or "Failed to process device data"
            )
        
        response = DeviceDataResponse(
            success=True,
            records_processed=result.records_collected,
            message="Device data processed successfully"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process device data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/upload-device-data", response_model=MobileDeviceDataResponse)
async def upload_device_data(
    request: MobileDeviceDataRequest,
    device_collector: DeviceDataCollector = Depends(get_device_collector)
):
    """
    Upload mobile device data from React Native app.
    
    This endpoint receives comprehensive device data collected by the mobile app,
    including device information, network status, and optional coarse location.
    It processes the data through the DeviceDataCollector for feature extraction
    and risk assessment.
    
    Args:
        request: Mobile device data payload with comprehensive device information
        device_collector: Configured device data collector for processing
        
    Returns:
        Processing results with success status and optional risk assessment
        
    Raises:
        HTTPException: If data validation fails or processing encounters errors
    """
    try:
        device_data = request.device_data
        logger.info(f"Processing mobile device data for user {device_data.user_id}")
        
        # Convert the Pydantic model to dictionary for collector processing
        device_data_dict = {
            "user_id": device_data.user_id,
            "device_info": {
                "model": device_data.device_info.model,
                "os": device_data.device_info.system_name,
                "os_version": device_data.device_info.system_version,
                "brand": device_data.device_info.brand,
                "manufacturer": device_data.device_info.manufacturer,
                "is_emulator": device_data.device_info.is_emulator,
                "platform": device_data.device_info.platform,
                "is_tablet": device_data.device_info.is_tablet,
                "has_security_features": device_data.device_info.is_pin_or_fingerprint_set,
                "total_memory": device_data.device_info.total_memory,
                "battery_level": device_data.device_info.battery_level
            },
            "network_info": {
                "type": device_data.network_info.type,
                "is_connected": device_data.network_info.is_connected,
                "is_wifi_enabled": device_data.network_info.is_wifi_enabled,
                "cellular_generation": device_data.network_info.cellular_generation,
            },
            "screen_info": {
                "width": device_data.screen_info.screen_width,
                "height": device_data.screen_info.screen_height,
                "pixel_ratio": device_data.screen_info.pixel_ratio
            },
            "collection_metadata": {
                "timestamp": device_data.collection_timestamp,
                "profile_version": device_data.profile_version,
                "collection_time_ms": device_data.collection_time_ms
            }
        }
        
        # Add optional coarse location if provided
        if device_data.coarse_location:
            device_data_dict["location_data"] = {
                "latitude": device_data.coarse_location.latitude,
                "longitude": device_data.coarse_location.longitude,
                "accuracy": device_data.coarse_location.accuracy,
                "timestamp": device_data.coarse_location.timestamp,
                "source": device_data.coarse_location.source
            }
        
        # Add app information if provided
        if device_data.app_info:
            device_data_dict["app_usage"] = {
                "total_count": device_data.app_info.total_count,
                "has_banking_apps": device_data.app_info.has_banking_apps,
                "has_payment_apps": device_data.app_info.has_payment_apps,
                "has_financial_apps": device_data.app_info.has_financial_apps
            }
        
        # Add risk flags if provided
        if device_data.risk_flags:
            device_data_dict["risk_assessment"] = {
                "is_emulator": device_data.risk_flags.is_emulator,
                "is_rooted_or_jailbroken": device_data.risk_flags.is_rooted_or_jailbroken,
                "has_debugging_enabled": device_data.risk_flags.has_debugging_enabled,
                "has_security_features": device_data.risk_flags.has_security_features,
                "is_os_outdated": device_data.risk_flags.is_os_outdated
            }
        
        # Process data through collector
        result = device_collector.process_device_data(device_data_dict)
        
        if not result.success:
            logger.warning(f"Device data processing failed for user {device_data.user_id}: {result.error_message}")
            raise HTTPException(
                status_code=400,
                detail=result.error_message or "Failed to process mobile device data"
            )
        
        # Calculate basic risk assessment
        risk_assessment = {}
        if device_data.risk_flags:
            risk_score = 0
            risk_factors = []
            
            if device_data.risk_flags.is_emulator:
                risk_score += 40
                risk_factors.append("emulator_detected")
            
            if device_data.risk_flags.is_rooted_or_jailbroken:
                risk_score += 35
                risk_factors.append("device_compromised")
            
            if device_data.risk_flags.has_debugging_enabled:
                risk_score += 20
                risk_factors.append("debugging_enabled")
            
            if not device_data.risk_flags.has_security_features:
                risk_score += 15
                risk_factors.append("no_security_features")
            
            if device_data.risk_flags.is_os_outdated:
                risk_score += 10
                risk_factors.append("outdated_os")
            
            risk_level = "low"
            if risk_score >= 70:
                risk_level = "high"
            elif risk_score >= 40:
                risk_level = "medium"
            
            risk_assessment = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "assessment_timestamp": datetime.utcnow().isoformat()
            }
        
        logger.info(f"Successfully processed mobile device data for user {device_data.user_id}")
        
        response = MobileDeviceDataResponse(
            success=True,
            message="Mobile device data processed successfully",
            user_id=device_data.user_id,
            records_processed=result.records_collected,
            risk_assessment=risk_assessment if risk_assessment else None
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process mobile device data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status")
async def get_collectors_status(
    aa_collector: AccountAggregatorCollector = Depends(get_aa_collector),
    device_collector: DeviceDataCollector = Depends(get_device_collector)
):
    """
    Get the status of all data collectors.
    
    Returns:
        Status information for all collectors
    """
    try:
        return {
            "account_aggregator": aa_collector.get_status(),
            "device_data": device_collector.get_status(),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get collector status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/webhook/aa-consent")
async def aa_consent_webhook(request: Dict[str, Any]):
    """
    Webhook endpoint for Account Aggregator consent notifications.
    
    This endpoint receives notifications about consent status changes
    from the AA provider.
    
    Args:
        request: Webhook payload from AA provider
        
    Returns:
        Acknowledgment response
    """
    try:
        logger.info(f"Received AA consent webhook: {request}")
        
        # Process webhook notification
        consent_id = request.get("consentId")
        status = request.get("status")
        
        if consent_id and status:
            # Update consent status in collector
            # This would typically update a database record
            logger.info(f"Consent {consent_id} status updated to: {status}")
        
        return JSONResponse(content={
            "status": "received",
            "message": "Webhook processed successfully"
        })
        
    except Exception as e:
        logger.error(f"Failed to process webhook: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process webhook"
        )
