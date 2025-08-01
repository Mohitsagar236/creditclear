@echo off
REM Docker Build and Run Script for Credit Risk Assessment System (Windows)

setlocal enabledelayedexpansion

echo 🐳 Docker Setup for Credit Risk Assessment System
echo =================================================

if "%1"=="build" goto build
if "%1"=="start" goto start
if "%1"=="dev" goto dev
if "%1"=="backend" goto backend
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="logs" goto logs
if "%1"=="status" goto status
goto help

:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)
echo ✅ Docker is running
goto :eof

:build
call :check_docker
echo 🔨 Building Docker image...
docker build -t credit-risk-backend .
if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)
echo ✅ Docker image built successfully
goto end

:start
call :check_docker
echo 🚀 Starting full application stack...
echo ⚠️ Trying simplified startup - API only...
docker-compose up -d api
echo ✅ Backend services started
echo.
echo 📊 Services running:
echo    - FastAPI Backend: http://localhost:8000
echo    - API Documentation: http://localhost:8000/docs
echo    - MLflow UI: http://localhost:5000
echo    - Redis: localhost:6379
echo.
echo 📋 To check status: docker-compose ps
echo 📋 To view logs: docker-compose logs -f backend
echo 📋 To stop services: docker-compose down
goto end

:dev
call :check_docker
echo 🔧 Starting development environment...
docker-compose --profile development up -d
echo ✅ Development environment started
echo.
echo 📊 Services running:
echo    - FastAPI Backend: http://localhost:8000 (with hot reload)
echo    - React Frontend: http://localhost:3000
echo    - API Documentation: http://localhost:8000/docs
echo    - Jupyter Lab: http://localhost:8888
echo    - MLflow UI: http://localhost:5000
goto end

:backend
call :check_docker
echo ⚡ Starting backend services only...
docker-compose up -d redis backend celery-worker
echo ✅ Backend services started
goto end

:stop
echo 🛑 Stopping all services...
docker-compose down
echo ✅ All services stopped
goto end

:clean
echo 🧹 Cleaning up containers and volumes...
docker-compose down -v --remove-orphans
docker system prune -f
echo ✅ Cleanup completed
goto end

:logs
echo 📋 Showing logs for all services...
docker-compose logs -f
goto end

:status
echo 📊 Service Status:
docker-compose ps
echo.
echo 🔍 Container Health:
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
goto end

:help
echo Usage: %0 [OPTION]
echo.
echo Options:
echo   build      Build the Docker image
echo   start      Start full application stack (production)
echo   dev        Start development environment with frontend
echo   backend    Start backend services only
echo   stop       Stop all services
echo   clean      Stop and remove all containers and volumes
echo   logs       Show logs for all services
echo   status     Show status of all services
echo   help       Show this help message
echo.
echo Examples:
echo   %0 build ^&^& %0 start     # Build and start production
echo   %0 dev                     # Start development environment
echo   %0 backend                 # Start backend only

:end
pause
