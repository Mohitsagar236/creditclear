#!/bin/bash

# Credit Risk Model System Startup Script
# This script helps start all components of the credit risk assessment system

echo "🏁 Starting Credit Risk Assessment System"
echo "========================================"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command_exists python; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

if ! command_exists node; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command_exists redis-server; then
    echo "⚠️  Redis not found. Please install Redis for async processing"
    echo "   On macOS: brew install redis"
    echo "   On Ubuntu: sudo apt-get install redis-server"
    echo "   On Windows: Use Docker or WSL"
fi

echo "✅ Prerequisites check complete"

# Setup Python environment
echo ""
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt

# Setup React frontend
echo ""
echo "⚛️  Setting up React frontend..."
cd src/dashboard

if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env.local" ]; then
    cp .env.example .env.local
    echo "📝 Created .env.local - please update API_BASE_URL if needed"
fi

cd ../..

echo ""
echo "🚀 Starting system components..."
echo ""

# Start Redis (if available)
if command_exists redis-server; then
    echo "Starting Redis server..."
    redis-server --daemonize yes
    echo "✅ Redis started"
else
    echo "⚠️  Please start Redis manually in a separate terminal:"
    echo "   redis-server"
fi

# Start Celery worker
echo ""
echo "Starting Celery worker..."
echo "Run this in a separate terminal:"
echo "celery -A src.api.celery_app worker --loglevel=info"

# Start FastAPI backend
echo ""
echo "Starting FastAPI backend..."
echo "Run this in a separate terminal:"
echo "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

# Start React frontend
echo ""
echo "Starting React frontend..."
echo "Run this in a separate terminal:"
echo "cd src/dashboard && npm run dev"

echo ""
echo "🎉 Setup complete! To start the system:"
echo ""
echo "1. Start Redis (if not already running):"
echo "   redis-server"
echo ""
echo "2. Start Celery worker:"
echo "   celery -A src.api.celery_app worker --loglevel=info"
echo ""
echo "3. Start FastAPI backend:"
echo "   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Start React frontend:"
echo "   cd src/dashboard && npm run dev"
echo ""
echo "📱 Access the dashboard at: http://localhost:3000"
echo "🔧 API documentation at: http://localhost:8000/docs"
echo ""
echo "Happy analyzing! 📊"
