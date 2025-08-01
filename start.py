#!/usr/bin/env python3
"""
Quick start script for the Credit Risk Model system.

This script helps users quickly set up and start the credit risk model system.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Print the startup banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         🏦 Credit Risk Model - Quick Start 🚀           ║
║                                                           ║
║    Comprehensive credit assessment with alternative data  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.9+")
        return False

def check_dependencies():
    """Check if required dependencies are installed."""
    print("\\n📦 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pandas',
        'numpy',
        'scikit-learn',
        'lightgbm',
        'xgboost'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - Missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def install_dependencies(missing_packages):
    """Install missing dependencies."""
    print("\\n🔧 Installing missing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        
        print("  ✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install dependencies: {e}")
        return False

def check_directories():
    """Check and create necessary directories."""
    print("\\n📁 Checking directories...")
    
    directories = [
        "data/raw",
        "data/processed", 
        "data/synthetic",
        "logs",
        "models"
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Created: {directory}")
        else:
            print(f"  ✅ Exists: {directory}")

def start_api_server():
    """Start the FastAPI server."""
    print("\\n🚀 Starting API server...")
    print("  📍 Server will be available at: http://localhost:8000")
    print("  📖 API documentation at: http://localhost:8000/docs")
    print("  🔍 Health check at: http://localhost:8000/health")
    print("\\n  Press Ctrl+C to stop the server\\n")
    
    try:
        # Change to project directory
        os.chdir(Path(__file__).parent)
        
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\\n\\n👋 Server stopped by user")
    except Exception as e:
        print(f"\\n❌ Failed to start server: {e}")

def show_usage_info():
    """Show usage information."""
    usage_info = """
🎯 SYSTEM READY! Here's what you can do:

📍 API Endpoints:
  • Health Check: GET http://localhost:8000/health
  • Predict Risk:  POST http://localhost:8000/api/v1/predict
  • Data Collection: POST http://localhost:8000/api/v1/collect-data
  • Device Analytics: POST http://localhost:8000/api/v1/device-analytics

📊 Dashboard:
  • Open: src/dashboard/index.html in your browser
  • Or run: cd src/dashboard && npm start (if Node.js installed)

🧪 Testing:
  • Run system tests: python system_test.py
  • Run specific tests: python -m pytest tests/

📚 Documentation:
  • API Docs: http://localhost:8000/docs
  • Project Status: PROJECT_STATUS.md
  • Implementation: AA_IMPLEMENTATION_SUMMARY.md

🔧 Development:
  • Format code: python -m black src/
  • Type check: python -m mypy src/
  • Lint code: python -m flake8 src/

📦 Docker Deployment:
  • Build: docker build -t credit-risk-model .
  • Run: docker-compose up -d
  • Stop: docker-compose down
"""
    print(usage_info)

def main():
    """Main startup function."""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\\n❌ Please upgrade to Python 3.9 or higher")
        sys.exit(1)
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print(f"\\n⚠️  Missing packages: {', '.join(missing)}")
        install_deps = input("\\n🤔 Install missing dependencies? (y/N): ").lower().strip()
        
        if install_deps in ['y', 'yes']:
            if not install_dependencies(missing):
                print("\\n❌ Failed to install dependencies. Please install manually:")
                print("   pip install -r requirements.txt")
                sys.exit(1)
        else:
            print("\\n❌ Please install dependencies manually:")
            print("   pip install -r requirements.txt")
            sys.exit(1)
    
    # Check directories
    check_directories()
    
    # Show options
    print("\\n🎛️  What would you like to do?")
    print("  1. Start API server (recommended)")
    print("  2. Run system tests")
    print("  3. Show usage information")
    print("  4. Exit")
    
    while True:
        choice = input("\\n👉 Enter your choice (1-4): ").strip()
        
        if choice == "1":
            start_api_server()
            break
        elif choice == "2":
            print("\\n🧪 Running system tests...")
            try:
                subprocess.run([sys.executable, "system_test.py"])
            except Exception as e:
                print(f"❌ Test execution failed: {e}")
            break
        elif choice == "3":
            show_usage_info()
            break
        elif choice == "4":
            print("\\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
