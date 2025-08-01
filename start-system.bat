@echo off
REM Credit Risk Model System Startup Script for Windows
REM This script helps start all components of the credit risk assessment system

echo 🏁 Starting Credit Risk Assessment System
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo ✅ Prerequisites check complete

REM Setup Python environment
echo.
echo 🐍 Setting up Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt

REM Setup React frontend
echo.
echo ⚛️  Setting up React frontend...
cd src\dashboard

if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)

REM Copy environment file if it doesn't exist
if not exist ".env.local" (
    copy .env.example .env.local
    echo 📝 Created .env.local - please update API_BASE_URL if needed
)

cd ..\..

echo.
echo 🚀 System setup complete!
echo.
echo To start the system, open these commands in separate terminals:
echo.
echo 1. Start Redis (using Docker):
echo    docker run -p 6379:6379 redis:alpine
echo.
echo 2. Start Celery worker:
echo    call venv\Scripts\activate
echo    celery -A src.api.celery_app worker --loglevel=info
echo.
echo 3. Start FastAPI backend:
echo    call venv\Scripts\activate
echo    uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo 4. Start React frontend:
echo    cd src\dashboard
echo    npm run dev
echo.
echo 📱 Access the dashboard at: http://localhost:3000
echo 🔧 API documentation at: http://localhost:8000/docs
echo.
echo Happy analyzing! 📊
pause
