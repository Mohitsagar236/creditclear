#!/bin/bash

# Credit Risk Assessment - Docker Compose Startup Script

echo "🚀 Starting Credit Risk Assessment System..."

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/models data/processed data/raw logs config

# Set proper permissions
echo "🔒 Setting permissions..."
chmod -R 755 data logs config

# Start the services
echo "🐳 Starting Docker services..."

# Start core services first (db, cache)
echo "  Starting database and cache..."
docker-compose up -d db cache

# Wait for database to be ready
echo "  Waiting for database to be ready..."
sleep 10

# Start API and worker
echo "  Starting API and worker services..."
docker-compose up -d api worker

# Wait for API to be ready
echo "  Waiting for API to be ready..."
sleep 15

# Start dashboard
echo "  Starting dashboard..."
docker-compose up -d dashboard

# Start optional services for development
if [ "$1" = "dev" ]; then
    echo "  Starting development services (MLflow)..."
    docker-compose --profile development up -d mlflow
fi

echo ""
echo "✅ Credit Risk Assessment System is starting up!"
echo ""
echo "🌐 Services will be available at:"
echo "  - API Backend: http://localhost:8000"
echo "  - Dashboard: http://localhost:3000"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
if [ "$1" = "dev" ]; then
    echo "  - MLflow: http://localhost:5000"
fi
echo ""
echo "📊 To view logs: docker-compose logs -f [service_name]"
echo "🛑 To stop: docker-compose down"
echo "🗑️  To cleanup: docker-compose down -v --remove-orphans"
echo ""
echo "⏳ Please wait a few moments for all services to fully initialize..."
