#!/usr/bin/env python3
"""
Simple backend server to test the digital footprint functionality
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Credit Risk API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Credit Risk Assessment API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics():
    """Endpoint to provide system metrics for monitoring"""
    return {
        "api_version": "1.0.0",
        "active_connections": 1,
        "requests_per_second": 0.5,
        "average_response_time_ms": 120,
        "status": "healthy"
    }

@app.post("/api/digital-footprint")
async def process_digital_footprint(data: dict):
    """Simple endpoint to receive digital footprint data"""
    print("Received digital footprint data:", data)
    
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

if __name__ == "__main__":
    print(" Starting Credit Risk Assessment API...")
    print(" Frontend: http://localhost:5173")
    print(" Backend API: http://localhost:8000")
    print(" API Docs: http://localhost:8000/docs")
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        print(f"ERROR starting backend: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
