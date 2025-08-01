# Account Aggregator Flow Implementation

This document describes the implementation of the Account Aggregator (AA) flow using the Setu AA API for collecting financial data with user consent.

## Overview

The Account Aggregator framework enables secure financial data sharing between Financial Information Providers (FIPs) like banks and Financial Information Users (FIUs) like lending platforms, with explicit user consent.

## Implementation Components

### 1. Enhanced AccountAggregatorCollector Class

**Location:** `src/data_processing/collectors.py`

**Key Features:**
- Full Setu AA API integration
- Consent lifecycle management
- FI data request and fetching
- Comprehensive error handling
- Data processing and validation

**Core Methods:**

#### `create_consent_request(user_id, fi_types, purpose, duration_days, customer_mobile, customer_name)`
- Creates a consent request with the Setu AA API
- Prepares POST request to `/consents` endpoint
- Generates proper Setu consent payload structure
- Returns ConsentRequest with consent URL for user approval

```python
consent = aa_collector.create_consent_request(
    user_id="user123",
    fi_types=["DEPOSIT", "TERM_DEPOSIT"],
    purpose="Credit Assessment",
    duration_days=30,
    customer_mobile="9876543210",
    customer_name="John Doe"
)
```

#### `get_consent_status(consent_handle)`
- Checks consent status via GET request to `/Consent/handle/{consentHandle}`
- Maps Setu status values to internal ConsentStatus enum
- Handles consent expiration and validation

```python
status = aa_collector.get_consent_status(consent_handle)
# Returns: PENDING, GRANTED, DENIED, EXPIRED, or REVOKED
```

#### `request_fi_data(consent_handle)`
- Initiates FI data collection via POST to `/FI/request`
- Requires granted consent
- Returns session ID for data fetching

```python
result = aa_collector.request_fi_data(consent_handle)
session_id = result["session_id"]
```

#### `fetch_fi_data(session_id)`
- Fetches actual financial data via GET to `/FI/fetch/{session_id}`
- Processes Setu FI data format into structured DataFrame
- Handles transaction data, account summaries, and metadata

### 2. Setu Consent Request Structure

**Class:** `SetuConsentRequest`

Implements the complete Setu AA consent request payload format:

```json
{
  "consentStart": "2024-01-15T10:00:00Z",
  "consentExpiry": "2024-02-14T10:00:00Z",
  "consentMode": "STORE",
  "fetchType": "PERIODIC",
  "consentTypes": ["TRANSACTIONS", "PROFILE", "SUMMARY"],
  "fiTypes": ["DEPOSIT", "TERM_DEPOSIT"],
  "DataConsumer": {
    "id": "your_client_id",
    "type": "FIU"
  },
  "DataProvider": {
    "id": "SETU-FIP",
    "type": "FIP"
  },
  "Customer": {
    "id": "9876543210",
    "Identifiers": [
      {
        "type": "MOBILE",
        "value": "9876543210"
      }
    ]
  },
  "Purpose": {
    "code": "101",
    "refUri": "https://api.rebit.org.in/aa/purpose/101.xml",
    "text": "Credit Assessment"
  },
  "FIDataRange": {
    "from": "2023-01-15T10:00:00Z",
    "to": "2024-01-15T10:00:00Z"
  },
  "Frequency": {
    "unit": "MONTH",
    "value": 1
  },
  "DataLife": {
    "unit": "MONTH",
    "value": 3
  }
}
```

### 3. FastAPI Routes

**Location:** `src/api/routes/data_collection.py`

#### Core Endpoints:

1. **POST /data-collection/initiate-aa-flow**
   - Initiates AA consent flow
   - Returns consent URL for user redirection
   - Validates input parameters

2. **GET /data-collection/consent-status**
   - Checks current consent status
   - Takes consent_handle as parameter

3. **POST /data-collection/request-fi-data**
   - Requests FI data collection
   - Returns session ID for data fetching

4. **GET /data-collection/fetch-fi-data/{session_id}**
   - Fetches actual financial data
   - Returns processed data in JSON format

5. **POST /data-collection/webhook/aa-consent**
   - Webhook for consent status notifications
   - Processes updates from Setu AA

#### Request/Response Models:

```python
class AAConsentRequest(BaseModel):
    user_id: str
    customer_mobile: str
    customer_name: Optional[str]
    fi_types: List[str] = ["DEPOSIT", "TERM_DEPOSIT"]
    purpose: str = "Credit Assessment"
    duration_days: int = 30

class AAConsentResponse(BaseModel):
    success: bool
    consent_handle: str
    consent_id: Optional[str]
    consent_url: Optional[str]
    status: str
    message: str
    expires_at: datetime
```

## Usage Flow

### 1. Complete AA Flow Example

```python
# Initialize and configure collector
aa_collector = AccountAggregatorCollector()
config = {
    "api_base_url": "https://fiu-uat.setu.co",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "webhook_url": "https://your-domain.com/webhook/aa-consent"
}
aa_collector.configure(config)

# Step 1: Create consent request
consent = aa_collector.create_consent_request(
    user_id="user123",
    customer_mobile="9876543210",
    fi_types=["DEPOSIT", "TERM_DEPOSIT"]
)

# Step 2: Redirect user to consent.consent_url for approval
print(f"Redirect user to: {consent.consent_url}")

# Step 3: Check consent status (poll until granted)
while True:
    status = aa_collector.get_consent_status(consent.consent_handle)
    if status == ConsentStatus.GRANTED:
        break
    elif status in [ConsentStatus.DENIED, ConsentStatus.EXPIRED]:
        raise Exception("Consent not granted")
    time.sleep(5)

# Step 4: Request FI data
fi_result = aa_collector.request_fi_data(consent.consent_handle)
session_id = fi_result["session_id"]

# Step 5: Fetch financial data
data_result = aa_collector.fetch_fi_data(session_id)
financial_data = data_result.data  # pandas DataFrame
```

### 2. API Usage Example

```python
import requests

# Step 1: Initiate AA flow
response = requests.post("http://localhost:8000/data-collection/initiate-aa-flow", json={
    "user_id": "user123",
    "customer_mobile": "9876543210",
    "fi_types": ["DEPOSIT", "TERM_DEPOSIT"]
})
consent_data = response.json()
consent_handle = consent_data["consent_handle"]

# Step 2: Check consent status
response = requests.get("http://localhost:8000/data-collection/consent-status", 
                       params={"consent_handle": consent_handle})
status_data = response.json()

# Step 3: Request FI data (after consent granted)
response = requests.post("http://localhost:8000/data-collection/request-fi-data", json={
    "consent_handle": consent_handle
})
fi_data = response.json()
session_id = fi_data["session_id"]

# Step 4: Fetch data
response = requests.get(f"http://localhost:8000/data-collection/fetch-fi-data/{session_id}")
financial_data = response.json()
```

## Data Processing

### FI Data Structure

The implementation processes Setu FI data into a structured format:

```python
# Sample processed DataFrame columns:
columns = [
    "account_id", "account_type", "account_name", "masked_number",
    "current_balance", "available_balance", "transaction_id",
    "transaction_date", "amount", "transaction_type", "description",
    "balance_after_txn", "value_date", "reference"
]
```

### Features Extracted

The financial data can be used for:
- Transaction pattern analysis
- Cash flow assessment
- Balance trend analysis
- Account diversity evaluation
- Income stability assessment

## Configuration

### Environment Variables

```bash
# Setu AA Configuration
SETU_API_BASE_URL=https://fiu-uat.setu.co
SETU_CLIENT_ID=your_client_id
SETU_CLIENT_SECRET=your_client_secret
SETU_WEBHOOK_URL=https://your-domain.com/webhook/aa-consent

# API Configuration
API_BASE_URL=http://localhost:8000
```

### Configuration Object

```python
config = {
    "api_base_url": "https://fiu-uat.setu.co",
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "webhook_url": "https://your-domain.com/webhook/aa-consent",
    "consent_timeout": 300  # 5 minutes
}
```

## Testing

### Test Scripts

1. **test_aa_flow.py** - Tests direct collector methods
2. **test_aa_api.py** - Tests FastAPI endpoints

### Running Tests

```bash
# Test direct implementation
python test_aa_flow.py

# Test API endpoints (requires running server)
python -m uvicorn src.api.main:app --reload &
python test_aa_api.py
```

### Test Coverage

- ✅ Consent request creation
- ✅ Consent status monitoring
- ✅ FI data request initiation
- ✅ Financial data fetching
- ✅ Data processing and validation
- ✅ API endpoint functionality
- ✅ Error handling and edge cases

## Security Considerations

### Data Protection
- No sensitive data stored locally
- Consent handles used for session management
- Automatic consent expiration
- Secure API communication

### Authentication
- Client ID/Secret for Setu API
- Request signing (can be implemented)
- Webhook verification
- Rate limiting considerations

### Privacy
- User consent required for all data access
- Consent can be revoked by user
- Data retention policies
- Audit trail for data access

## Error Handling

### Common Error Scenarios
1. **Network connectivity issues**
2. **Invalid consent handles**
3. **Expired consents**
4. **API rate limits**
5. **Data parsing errors**

### Error Response Format
```python
{
    "success": False,
    "error": "error_code",
    "message": "Human readable error message",
    "details": {}  # Additional error context
}
```

## Integration with Credit Risk Model

The fetched financial data integrates with the existing feature engineering pipeline:

```python
from src.data_processing.feature_engineering import FeatureEngineer

# Process AA data
feature_engineer = FeatureEngineer()
financial_features = feature_engineer.create_financial_features(aa_data)

# Combine with other alternative data
combined_features = feature_engineer.combine_features([
    financial_features,
    mobility_features,
    device_features
])
```

## Production Deployment

### Infrastructure Requirements
- Redis for session management
- PostgreSQL for consent storage
- HTTPS endpoints for webhooks
- Load balancing for high availability

### Monitoring
- API response times
- Consent completion rates
- Data fetch success rates
- Error rate monitoring

### Compliance
- RBI AA guidelines compliance
- Data localization requirements
- Audit logging
- Consent management records

## Next Steps

1. **Enhanced Error Handling**: Implement retry mechanisms and circuit breakers
2. **Caching**: Add Redis caching for consent status
3. **Database Integration**: Store consent records in PostgreSQL
4. **Monitoring**: Add comprehensive logging and metrics
5. **Security**: Implement request signing and webhook verification
6. **Testing**: Add integration tests with Setu sandbox
7. **Documentation**: API documentation with OpenAPI/Swagger
