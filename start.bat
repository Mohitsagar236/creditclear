@echo off
REM Credit Risk Assessment - Docker Compose Startup Script for Windows

echo 🚀 Starting Credit Risk Assessment System...

REM Check if docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if docker-compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "data\models" mkdir data\models
if not exist "data\processed" mkdir data\processed
if not exist "data\raw" mkdir data\raw
if not exist "logs" mkdir logs
if not exist "config" mkdir config

REM Start the services
echo 🐳 Starting Docker services...

REM Start core services first (db, cache)
echo   Starting database and cache...
docker-compose up -d db cache

REM Wait for database to be ready
echo   Waiting for database to be ready...
timeout /t 10 /nobreak >nul

REM Start API and worker
echo   Starting API and worker services...
docker-compose up -d api worker

REM Wait for API to be ready
echo   Waiting for API to be ready...
timeout /t 15 /nobreak >nul

REM Start dashboard
echo   Starting dashboard...
docker-compose up -d dashboard

REM Start optional services for development
if "%1"=="dev" (
    echo   Starting development services (MLflow)...
    docker-compose --profile development up -d mlflow
)

echo.
echo ✅ Credit Risk Assessment System is starting up!
echo.
echo 🌐 Services will be available at:
echo   - API Backend: http://localhost:8000
echo   - Dashboard: http://localhost:3000
echo   - PostgreSQL: localhost:5432
echo   - Redis: localhost:6379
if "%1"=="dev" (
    echo   - MLflow: http://localhost:5000
)
echo.
echo 📊 To view logs: docker-compose logs -f [service_name]
echo 🛑 To stop: docker-compose down
echo 🗑️  To cleanup: docker-compose down -v --remove-orphans
echo.
echo ⏳ Please wait a few moments for all services to fully initialize...
