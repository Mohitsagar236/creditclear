#!/bin/bash

# Docker Build and Run Script for Credit Risk Assessment System

set -e

echo "🐳 Docker Setup for Credit Risk Assessment System"
echo "================================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to build the application
build_app() {
    echo "🔨 Building Docker image..."
    docker build -t credit-risk-backend .
    echo "✅ Docker image built successfully"
}

# Function to run the full stack
run_full_stack() {
    echo "🚀 Starting full application stack..."
    docker-compose up -d redis mlflow backend celery-worker
    echo "✅ Backend services started"
    
    echo "📊 Services running:"
    echo "   - FastAPI Backend: http://localhost:8000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo "   - MLflow UI: http://localhost:5000"
    echo "   - Redis: localhost:6379"
    
    echo ""
    echo "📋 To check status:"
    echo "   docker-compose ps"
    echo ""
    echo "📋 To view logs:"
    echo "   docker-compose logs -f backend"
    echo "   docker-compose logs -f celery-worker"
    echo ""
    echo "📋 To stop services:"
    echo "   docker-compose down"
}

# Function to run development environment
run_development() {
    echo "🔧 Starting development environment..."
    docker-compose --profile development up -d
    echo "✅ Development environment started"
    
    echo "📊 Services running:"
    echo "   - FastAPI Backend: http://localhost:8000 (with hot reload)"
    echo "   - React Frontend: http://localhost:3000"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo "   - Jupyter Lab: http://localhost:8888"
    echo "   - MLflow UI: http://localhost:5000"
}

# Function to run backend only
run_backend_only() {
    echo "⚡ Starting backend services only..."
    docker-compose up -d redis backend celery-worker
    echo "✅ Backend services started"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  build      Build the Docker image"
    echo "  start      Start full application stack (production)"
    echo "  dev        Start development environment with frontend"
    echo "  backend    Start backend services only"
    echo "  stop       Stop all services"
    echo "  clean      Stop and remove all containers and volumes"
    echo "  logs       Show logs for all services"
    echo "  status     Show status of all services"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build && $0 start     # Build and start production"
    echo "  $0 dev                   # Start development environment"
    echo "  $0 backend               # Start backend only"
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping all services..."
    docker-compose down
    echo "✅ All services stopped"
}

# Function to clean up
clean_up() {
    echo "🧹 Cleaning up containers and volumes..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo "✅ Cleanup completed"
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs for all services..."
    docker-compose logs -f
}

# Function to show status
show_status() {
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🔍 Container Health:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
}

# Main script logic
case "${1:-help}" in
    build)
        check_docker
        build_app
        ;;
    start)
        check_docker
        run_full_stack
        ;;
    dev)
        check_docker
        run_development
        ;;
    backend)
        check_docker
        run_backend_only
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_up
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    help|*)
        show_help
        ;;
esac
