from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class DigitalIdentity(BaseModel):
    deviceId: str
    emailVerified: bool
    phoneVerified: bool
    accountAge: int

class SocialMediaMetrics(BaseModel):
    networkSize: int
    accountAge: int
    activityMetrics: Dict[str, float]

class MobileUsage(BaseModel):
    appCategories: List[str]
    usageDuration: Dict[str, int]
    timePatterns: Dict[str, float]
    activeHours: List[int]

class EcommerceData(BaseModel):
    purchaseHistory: List[Dict]
    paymentMethods: List[str]
    transactionMetrics: Dict[str, float]

class DigitalPayments(BaseModel):
    upiTransactions: List[Dict]
    walletUsage: Dict[str, float]
    paymentPatterns: Dict[str, float]

class UtilityData(BaseModel):
    billPayments: List[Dict]
    subscriptions: List[str]
    paymentConsistency: float

class LocationData(BaseModel):
    homeWorkPattern: Dict[str, Dict]
    travelPatterns: Dict[str, float]
    locationStability: float
    frequentLocations: List[Dict]

class DeviceTechnical(BaseModel):
    device: Dict[str, str]
    apps: Dict[str, List[str]]
    network: Dict[str, float]
    security: Dict[str, float]

class DigitalFootprint(BaseModel):
    timestamp: datetime
    digitalIdentity: DigitalIdentity
    socialMedia: Optional[SocialMediaMetrics]
    mobileUsage: MobileUsage
    ecommerce: EcommerceData
    digitalPayments: DigitalPayments
    utilityServices: UtilityData
    locationMobility: Optional[LocationData]
    deviceTechnical: DeviceTechnical

class DigitalFootprintResponse(BaseModel):
    success: bool
    score: float
    insights: List[str]
    recommendations: List[str]
