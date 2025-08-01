#!/usr/bin/env python3
"""
Simple startup script for the Credit Risk API server.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the app
try:
    from src.api.main import app
    import uvicorn
    
    print("🚀 Starting Credit Risk API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Auto-reload: Enabled")
    print()
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
except Exception as e:
    print(f"❌ Error starting server: {e}")
    sys.exit(1)
