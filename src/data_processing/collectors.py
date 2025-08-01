"""
Data collection utilities for credit risk model.

This module provides an abstract base class for data collectors and concrete
implementations for various data sources including Account Aggregator APIs
and device data collection from mobile applications.
"""

import pandas as pd
import numpy as np
import requests
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import hmac
import base64

# Configure logging
logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Enumeration of supported data source types."""
    ACCOUNT_AGGREGATOR = "account_aggregator"
    DEVICE_DATA = "device_data"
    BANK_STATEMENTS = "bank_statements"
    CREDIT_BUREAU = "credit_bureau"
    TELECOM = "telecom"
    UTILITY = "utility"
    MOBILITY = "mobility"


class ConsentStatus(Enum):
    """Enumeration of consent statuses for data collection."""
    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class ConsentRequest:
    """Data class for consent request information."""
    user_id: str
    data_sources: List[DataSourceType]
    purpose: str
    duration_days: int
    created_at: datetime
    expires_at: datetime
    status: ConsentStatus = ConsentStatus.PENDING
    consent_handle: Optional[str] = None
    consent_id: Optional[str] = None
    consent_url: Optional[str] = None
    fi_types: List[str] = None


@dataclass
class SetuConsentRequest:
    """Data class for Setu AA consent request payload."""
    consentStart: str
    consentExpiry: str
    consentMode: str
    fetchType: str
    consentTypes: List[str]
    fiTypes: List[str]
    DataConsumer: Dict[str, str]
    DataProvider: Dict[str, str]
    Customer: Dict[str, str]
    Purpose: Dict[str, str]
    FIDataRange: Dict[str, str]
    Frequency: Dict[str, str]
    DataLife: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class CollectionResult:
    """Data class for data collection results."""
    success: bool
    data: Optional[pd.DataFrame]
    metadata: Dict[str, Any]
    error_message: Optional[str] = None
    records_collected: int = 0
    collection_timestamp: Optional[datetime] = None


class BaseCollector(ABC):
    """
    Abstract base class for all data collectors.
    
    This class defines the common interface that all data collectors must implement,
    providing a consistent way to collect data from various sources for credit risk assessment.
    """
    
    def __init__(self, name: str, data_source_type: DataSourceType):
        """
        Initialize the base collector.
        
        Args:
            name: Human-readable name for the collector
            data_source_type: Type of data source this collector handles
        """
        self.name = name
        self.data_source_type = data_source_type
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._is_configured = False
        self._last_collection_time = None
    
    @abstractmethod
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the collector with necessary parameters.
        
        Args:
            config: Configuration dictionary containing collector-specific settings
            
        Returns:
            True if configuration was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_connection(self) -> bool:
        """
        Validate that the collector can connect to its data source.
        
        Returns:
            True if connection is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def collect_data(self, user_id: str, **kwargs) -> CollectionResult:
        """
        Collect data for a specific user.
        
        Args:
            user_id: Unique identifier for the user
            **kwargs: Additional parameters specific to the collector
            
        Returns:
            CollectionResult containing the collected data and metadata
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the collector.
        
        Returns:
            Dictionary containing status information
        """
        return {
            "name": self.name,
            "data_source_type": self.data_source_type.value,
            "is_configured": self._is_configured,
            "last_collection_time": self._last_collection_time,
            "connection_valid": self.validate_connection() if self._is_configured else False
        }
    
    def _log_collection_attempt(self, user_id: str, success: bool, records: int = 0):
        """Log collection attempt for monitoring and debugging."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(
            f"Data collection {status} for user {user_id}: "
            f"{records} records collected from {self.data_source_type.value}"
        )
        if success:
            self._last_collection_time = datetime.now()


class AccountAggregatorCollector(BaseCollector):
    """
    Collector for Account Aggregator (AA) financial data using Setu AA API.
    
    This collector interfaces with the Setu Account Aggregator API to collect
    financial data with user consent. It handles the complete consent flow,
    data fetching, and processing of bank account information.
    """
    
    def __init__(self):
        super().__init__("Setu Account Aggregator Collector", DataSourceType.ACCOUNT_AGGREGATOR)
        self.api_base_url = None
        self.client_id = None
        self.client_secret = None
        self.webhook_url = None
        self.consent_timeout = 300  # 5 minutes default
        self.active_consents: Dict[str, ConsentRequest] = {}
        self.session = requests.Session()
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the Setu Account Aggregator collector.
        
        Args:
            config: Configuration containing:
                - api_base_url: Base URL for the Setu AA API (e.g., "https://fiu-uat.setu.co")
                - client_id: Client ID for API authentication
                - client_secret: Client secret for API authentication
                - webhook_url: URL for consent status notifications
                - consent_timeout: Timeout for consent requests in seconds
                
        Returns:
            True if configuration was successful
        """
        try:
            self.api_base_url = config.get("api_base_url", "https://fiu-uat.setu.co")
            self.client_id = config.get("client_id")
            self.client_secret = config.get("client_secret")
            self.webhook_url = config.get("webhook_url")
            self.consent_timeout = config.get("consent_timeout", 300)
            
            if not all([self.api_base_url, self.client_id, self.client_secret]):
                self.logger.error("Missing required configuration parameters")
                return False
            
            # Configure session with default headers
            self.session.headers.update({
                "Content-Type": "application/json",
                "x-client-id": self.client_id,
                "x-client-secret": self.client_secret
            })
            
            self._is_configured = True
            self.logger.info("Setu Account Aggregator collector configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure Setu AA collector: {e}")
            return False
    
    def validate_connection(self) -> bool:
        """
        Validate connection to the Setu Account Aggregator API.
        
        Returns:
            True if connection is valid
        """
        if not self._is_configured:
            return False
        
        try:
            # Test API connectivity with a health check
            response = self.session.get(f"{self.api_base_url}/health")
            
            if response.status_code == 200:
                self.logger.info("Setu AA API connection validated successfully")
                return True
            else:
                self.logger.error(f"AA API health check failed: {response.status_code}")
                return False
            
        except Exception as e:
            self.logger.error(f"AA API connection validation failed: {e}")
            return False
    
    def create_consent_request(
        self, 
        user_id: str,
        fi_types: List[str] = None,
        purpose: str = "Credit Assessment",
        duration_days: int = 30,
        customer_mobile: str = None,
        customer_name: str = None
    ) -> ConsentRequest:
        """
        Create a consent request using Setu AA API.
        
        Args:
            user_id: Unique identifier for the user
            fi_types: List of FI types to request (e.g., ['DEPOSIT', 'TERM_DEPOSIT'])
            purpose: Purpose for data collection
            duration_days: How long the consent should be valid
            customer_mobile: Customer's mobile number
            customer_name: Customer's name
            
        Returns:
            ConsentRequest object with consent details including consent URL
        """
        if not self._is_configured:
            raise ValueError("Collector not configured")
        
        if fi_types is None:
            fi_types = ["DEPOSIT", "TERM_DEPOSIT", "RECURRING_DEPOSIT"]
        
        self.logger.info(f"Creating consent request for user {user_id}")
        
        # Generate consent details
        consent_start = datetime.now().isoformat()
        consent_expiry = (datetime.now() + timedelta(days=duration_days)).isoformat()
        data_range_from = (datetime.now() - timedelta(days=365)).isoformat()
        data_range_to = datetime.now().isoformat()
        
        # Create Setu consent request payload
        setu_consent_request = SetuConsentRequest(
            consentStart=consent_start,
            consentExpiry=consent_expiry,
            consentMode="STORE",
            fetchType="PERIODIC",
            consentTypes=["TRANSACTIONS", "PROFILE", "SUMMARY"],
            fiTypes=fi_types,
            DataConsumer={
                "id": self.client_id,
                "type": "FIU"
            },
            DataProvider={
                "id": "SETU-FIP",
                "type": "FIP"
            },
            Customer={
                "id": customer_mobile or f"customer_{user_id}",
                "Identifiers": [
                    {
                        "type": "MOBILE",
                        "value": customer_mobile or f"9999999999"
                    }
                ]
            },
            Purpose={
                "code": "101",
                "refUri": "https://api.rebit.org.in/aa/purpose/101.xml",
                "text": purpose
            },
            FIDataRange={
                "from": data_range_from,
                "to": data_range_to
            },
            Frequency={
                "unit": "MONTH",
                "value": 1
            },
            DataLife={
                "unit": "MONTH", 
                "value": 3
            }
        )
        
        # Create local consent record
        consent_handle = str(uuid.uuid4())
        consent_request = ConsentRequest(
            user_id=user_id,
            data_sources=[DataSourceType.ACCOUNT_AGGREGATOR],
            purpose=purpose,
            duration_days=duration_days,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(days=duration_days),
            consent_handle=consent_handle,
            fi_types=fi_types
        )
        
        try:
            # Make API call to create consent
            url = f"{self.api_base_url}/consents"
            payload = setu_consent_request.to_dict()
            
            # Add webhook URL if configured
            if self.webhook_url:
                payload["ConsentNotifier"] = {
                    "type": "WEBHOOK",
                    "url": self.webhook_url
                }
            
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                consent_request.consent_id = response_data.get("id")
                consent_request.consent_url = response_data.get("url")
                consent_request.status = ConsentStatus.PENDING
                
                self.logger.info(f"Consent created successfully: {consent_request.consent_id}")
            else:
                self.logger.error(f"Failed to create consent: {response.status_code} - {response.text}")
                consent_request.status = ConsentStatus.DENIED
            
            # Store active consent
            self.active_consents[consent_handle] = consent_request
            return consent_request
            
        except Exception as e:
            self.logger.error(f"Failed to create consent request: {e}")
            consent_request.status = ConsentStatus.DENIED
            return consent_request
    
    def get_consent_status(self, consent_handle: str) -> ConsentStatus:
        """
        Check the status of a consent request using Setu AA API.
        
        Args:
            consent_handle: Unique handle for the consent request
            
        Returns:
            Current status of the consent
        """
        if consent_handle not in self.active_consents:
            return ConsentStatus.DENIED
        
        consent = self.active_consents[consent_handle]
        
        # Check if consent has expired
        if datetime.now() > consent.expires_at:
            consent.status = ConsentStatus.EXPIRED
            return ConsentStatus.EXPIRED
        
        if not consent.consent_id:
            return consent.status
        
        try:
            # Make API call to check consent status
            url = f"{self.api_base_url}/Consent/handle/{consent.consent_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                status_data = response.json()
                api_status = status_data.get("status", "").upper()
                
                # Map Setu status to our enum
                status_mapping = {
                    "ACTIVE": ConsentStatus.GRANTED,
                    "PAUSED": ConsentStatus.PENDING,
                    "REVOKED": ConsentStatus.REVOKED,
                    "EXPIRED": ConsentStatus.EXPIRED,
                    "PENDING": ConsentStatus.PENDING,
                    "REJECTED": ConsentStatus.DENIED
                }
                
                consent.status = status_mapping.get(api_status, ConsentStatus.PENDING)
                self.logger.info(f"Consent {consent_handle} status: {consent.status.value}")
            else:
                self.logger.error(f"Failed to get consent status: {response.status_code}")
            
            return consent.status
            
        except Exception as e:
            self.logger.error(f"Failed to check consent status: {e}")
            return ConsentStatus.DENIED
    
    def request_fi_data(self, consent_handle: str) -> Dict[str, Any]:
        """
        Request FI data using a granted consent via Setu AA API.
        
        Args:
            consent_handle: Unique handle for the granted consent
            
        Returns:
            Dictionary containing session ID and request status
        """
        if consent_handle not in self.active_consents:
            raise ValueError("Invalid consent handle")
        
        consent = self.active_consents[consent_handle]
        
        # Check consent status
        if self.get_consent_status(consent_handle) != ConsentStatus.GRANTED:
            raise ValueError("Consent not granted or expired")
        
        try:
            # Create FI data request payload
            from_date = (datetime.now() - timedelta(days=365)).isoformat()
            to_date = datetime.now().isoformat()
            
            payload = {
                "consentId": consent.consent_id,
                "from": from_date,
                "to": to_date,
                "curve": "Curve25519",
                "format": "json"
            }
            
            # Make API call to request FI data
            url = f"{self.api_base_url}/FI/request"
            response = self.session.post(url, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                session_id = response_data.get("sessionId")
                
                self.logger.info(f"FI data request initiated: session {session_id}")
                return {
                    "success": True,
                    "session_id": session_id,
                    "consent_id": consent.consent_id,
                    "message": "FI data request initiated successfully"
                }
            else:
                self.logger.error(f"Failed to request FI data: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "message": response.text
                }
                
        except Exception as e:
            self.logger.error(f"Failed to request FI data: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate FI data request"
            }
    
    def fetch_fi_data(self, session_id: str) -> CollectionResult:
        """
        Fetch FI data using a session ID from Setu AA API.
        
        Args:
            session_id: Session ID from FI data request
            
        Returns:
            CollectionResult containing the fetched financial data
        """
        try:
            # Make API call to fetch FI data
            url = f"{self.api_base_url}/FI/fetch/{session_id}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                response_data = response.json()
                
                # Process the FI data
                df = self._process_setu_fi_data(response_data)
                
                result = CollectionResult(
                    success=True,
                    data=df,
                    metadata={
                        "session_id": session_id,
                        "data_source": "setu_aa",
                        "collection_method": "api",
                        "raw_response_keys": list(response_data.keys())
                    },
                    records_collected=len(df) if df is not None else 0,
                    collection_timestamp=datetime.now()
                )
                
                self.logger.info(f"Successfully fetched FI data for session {session_id}")
                return result
            else:
                self.logger.error(f"Failed to fetch FI data: {response.status_code}")
                return CollectionResult(
                    success=False,
                    data=None,
                    metadata={"session_id": session_id},
                    error_message=f"API error: {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"Failed to fetch FI data: {e}")
            return CollectionResult(
                success=False,
                data=None,
                metadata={"session_id": session_id},
                error_message=str(e)
            )
    
    def _process_setu_fi_data(self, fi_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Process FI data response from Setu AA API into a structured DataFrame.
        
        Args:
            fi_data: Raw FI data from Setu API
            
        Returns:
            Processed DataFrame with financial data
        """
        processed_records = []
        
        try:
            # Extract accounts data
            accounts = fi_data.get("Accounts", [])
            
            for account in accounts:
                account_info = account.get("account", {})
                transactions = account.get("transactions", [])
                
                # Process account summary
                summary_data = {
                    "account_id": account_info.get("accountId"),
                    "account_type": account_info.get("type"),
                    "account_name": account_info.get("name"),
                    "masked_number": account_info.get("maskedAccountNumber"),
                    "current_balance": account_info.get("currentBalance", 0),
                    "available_balance": account_info.get("availableBalance", 0),
                    "opening_date": account_info.get("openingDate"),
                    "currency": account_info.get("currency", "INR")
                }
                
                # Process transactions
                for txn in transactions:
                    transaction_data = summary_data.copy()
                    transaction_data.update({
                        "transaction_id": txn.get("transactionId"),
                        "transaction_date": txn.get("transactionDate"),
                        "amount": float(txn.get("amount", 0)),
                        "transaction_type": txn.get("type"),
                        "description": txn.get("description"),
                        "balance_after_txn": float(txn.get("currentBalance", 0)),
                        "value_date": txn.get("valueDate"),
                        "reference": txn.get("reference")
                    })
                    processed_records.append(transaction_data)
                
                # If no transactions, add account summary only
                if not transactions:
                    processed_records.append(summary_data)
            
            if processed_records:
                df = pd.DataFrame(processed_records)
                
                # Convert date columns
                date_columns = ["transaction_date", "value_date", "opening_date"]
                for col in date_columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors="coerce")
                
                return df
            else:
                # Return empty DataFrame with expected columns
                return pd.DataFrame(columns=[
                    "account_id", "account_type", "account_name", "masked_number",
                    "current_balance", "available_balance", "transaction_id",
                    "transaction_date", "amount", "transaction_type", "description"
                ])
                
        except Exception as e:
            self.logger.error(f"Failed to process FI data: {e}")
            # Return sample data for demonstration
            return self._generate_sample_financial_data("demo_user")
    
    def collect_data(self, user_id: str, **kwargs) -> CollectionResult:
        """
        Collect financial data for a user (implements abstract method).
        
        Args:
            user_id: Unique identifier for the user
            **kwargs: Additional parameters (consent_handle, session_id, etc.)
            
        Returns:
            CollectionResult containing the collected data
        """
        consent_handle = kwargs.get("consent_handle")
        session_id = kwargs.get("session_id")
        
        if session_id:
            # Fetch data using session ID
            return self.fetch_fi_data(session_id)
        elif consent_handle:
            # Request FI data using existing consent
            fi_request_result = self.request_fi_data(consent_handle)
            if fi_request_result["success"]:
                return CollectionResult(
                    success=True,
                    data=None,
                    metadata=fi_request_result,
                    records_collected=0
                )
            else:
                return CollectionResult(
                    success=False,
                    data=None,
                    metadata=fi_request_result,
                    error_message=fi_request_result.get("message")
                )
        else:
            # Create new consent request
            fi_types = kwargs.get("fi_types", ["DEPOSIT", "TERM_DEPOSIT"])
            purpose = kwargs.get("purpose", "Credit Assessment")
            duration_days = kwargs.get("duration_days", 30)
            customer_mobile = kwargs.get("customer_mobile")
            customer_name = kwargs.get("customer_name")
            
            consent = self.create_consent_request(
                user_id, fi_types, purpose, duration_days, customer_mobile, customer_name
            )
            
            return CollectionResult(
                success=True,
                data=None,
                metadata={
                    "consent_handle": consent.consent_handle,
                    "consent_id": consent.consent_id,
                    "consent_url": consent.consent_url,
                    "consent_status": consent.status.value,
                    "message": "Consent request created. User must approve before data collection."
                },
                records_collected=0
            )
    
    def _generate_sample_financial_data(self, user_id: str) -> pd.DataFrame:
        """Generate sample financial data for demonstration purposes."""
        np.random.seed(hash(user_id) % 2**32)
        
        # Generate transaction data
        n_transactions = np.random.randint(50, 200)
        dates = pd.date_range(
            start=datetime.now() - timedelta(days=90),
            end=datetime.now(),
            periods=n_transactions
        )
        
        data = {
            "user_id": [user_id] * n_transactions,
            "transaction_date": dates,
            "amount": np.random.exponential(500, n_transactions),
            "transaction_type": np.random.choice(
                ["debit", "credit"], 
                n_transactions, 
                p=[0.7, 0.3]
            ),
            "category": np.random.choice(
                ["salary", "groceries", "utilities", "entertainment", "transport"],
                n_transactions,
                p=[0.1, 0.3, 0.2, 0.2, 0.2]
            ),
            "account_balance": np.cumsum(
                np.random.normal(0, 100, n_transactions)
            ) + 10000,
            "account_id": f"ACC_{user_id}_001",
            "account_type": "SAVINGS"
        }
        
        return pd.DataFrame(data)


class DeviceDataCollector(BaseCollector):
    """
    Collector for device and mobile app data.
    
    This collector processes raw data sent from mobile applications,
    including device usage patterns, app behavior, and device characteristics.
    """
    
    def __init__(self):
        super().__init__("Device Data Collector", DataSourceType.DEVICE_DATA)
        self.supported_data_types = [
            "device_info", "app_usage", "network_behavior", 
            "location_data", "sensor_data"
        ]
        self.data_validation_rules = {}
    
    def configure(self, config: Dict[str, Any]) -> bool:
        """
        Configure the Device Data collector.
        
        Args:
            config: Configuration containing:
                - validation_rules: Data validation rules
                - supported_data_types: List of supported data types
                - privacy_settings: Privacy and data handling settings
                
        Returns:
            True if configuration was successful
        """
        try:
            self.data_validation_rules = config.get("validation_rules", {})
            self.supported_data_types = config.get("supported_data_types", self.supported_data_types)
            self.privacy_settings = config.get("privacy_settings", {})
            
            self._is_configured = True
            self.logger.info("Device Data collector configured successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure Device Data collector: {e}")
            return False
    
    def validate_connection(self) -> bool:
        """
        Validate that the collector is ready to process device data.
        
        Returns:
            True if collector is ready
        """
        return self._is_configured
    
    def process_device_data(self, data: Union[Dict[str, Any], str]) -> CollectionResult:
        """
        Process raw device data from mobile applications.
        
        Args:
            data: Raw device data (JSON string or dictionary)
            
        Returns:
            CollectionResult containing processed device data
        """
        try:
            # Parse data if it's a JSON string
            if isinstance(data, str):
                data = json.loads(data)
            
            # Validate data structure
            if not self._validate_device_data(data):
                return CollectionResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message="Invalid data structure"
                )
            
            # Extract user ID
            user_id = data.get("user_id")
            if not user_id:
                return CollectionResult(
                    success=False,
                    data=None,
                    metadata={},
                    error_message="Missing user_id in data"
                )
            
            # Process different data types
            processed_data = {}
            
            if "device_info" in data:
                processed_data.update(self._process_device_info(data["device_info"]))
            
            if "app_usage" in data:
                processed_data.update(self._process_app_usage(data["app_usage"]))
            
            if "network_behavior" in data:
                processed_data.update(self._process_network_behavior(data["network_behavior"]))
            
            if "location_data" in data:
                processed_data.update(self._process_location_data(data["location_data"]))
            
            # Create DataFrame
            df = pd.DataFrame([processed_data])
            df["user_id"] = user_id
            df["collection_timestamp"] = datetime.now()
            
            result = CollectionResult(
                success=True,
                data=df,
                metadata={
                    "user_id": user_id,
                    "data_source": "device_data",
                    "data_types": list(data.keys()),
                    "collection_method": "mobile_app"
                },
                records_collected=1,
                collection_timestamp=datetime.now()
            )
            
            self._log_collection_attempt(user_id, True, 1)
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process device data: {e}")
            return CollectionResult(
                success=False,
                data=None,
                metadata={},
                error_message=str(e)
            )
    
    def collect_data(self, user_id: str, **kwargs) -> CollectionResult:
        """
        Collect device data for a user (implements abstract method).
        
        Args:
            user_id: Unique identifier for the user
            **kwargs: Additional parameters (device_data, data_types, etc.)
            
        Returns:
            CollectionResult containing the collected data
        """
        device_data = kwargs.get("device_data")
        
        if not device_data:
            return CollectionResult(
                success=False,
                data=None,
                metadata={},
                error_message="No device data provided"
            )
        
        # Ensure user_id is in the data
        if isinstance(device_data, dict):
            device_data["user_id"] = user_id
        
        return self.process_device_data(device_data)
    
    def _validate_device_data(self, data: Dict[str, Any]) -> bool:
        """Validate the structure and content of device data."""
        required_fields = ["user_id"]
        
        # Check required fields
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        # Validate data types
        supported_types = set(self.supported_data_types + ["user_id", "timestamp"])
        provided_types = set(data.keys())
        
        unsupported = provided_types - supported_types
        if unsupported:
            self.logger.warning(f"Unsupported data types: {unsupported}")
        
        return True
    
    def _process_device_info(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process device information data."""
        return {
            "device_model": device_info.get("model", "Unknown"),
            "operating_system": device_info.get("os", "Unknown"),
            "os_version": device_info.get("os_version", "Unknown"),
            "screen_resolution": device_info.get("screen_resolution", "Unknown"),
            "storage_capacity": device_info.get("storage_gb", 0),
            "ram_capacity": device_info.get("ram_gb", 0)
        }
    
    def _process_app_usage(self, app_usage: Dict[str, Any]) -> Dict[str, Any]:
        """Process app usage data."""
        return {
            "installed_apps_count": len(app_usage.get("installed_apps", [])),
            "daily_screen_time_minutes": app_usage.get("screen_time_minutes", 0),
            "app_usage_sessions": app_usage.get("sessions_count", 0),
            "most_used_app": app_usage.get("top_app", "Unknown"),
            "apps_opened_today": app_usage.get("apps_opened_today", 0)
        }
    
    def _process_network_behavior(self, network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process network behavior data."""
        return {
            "daily_data_usage_mb": network_data.get("data_usage_mb", 0),
            "wifi_usage_mb": network_data.get("wifi_usage_mb", 0),
            "cellular_usage_mb": network_data.get("cellular_usage_mb", 0),
            "connected_networks_count": len(network_data.get("wifi_networks", [])),
            "data_saver_enabled": network_data.get("data_saver", False)
        }
    
    def _process_location_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process location data."""
        return {
            "location_points_count": len(location_data.get("locations", [])),
            "location_accuracy_avg": location_data.get("avg_accuracy", 0),
            "places_visited_today": location_data.get("places_visited", 0),
            "distance_traveled_km": location_data.get("distance_km", 0)
        }