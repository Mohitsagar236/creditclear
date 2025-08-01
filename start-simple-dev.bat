@echo off
REM Credit Risk Assessment - Development Startup Script for Windows (Using Simple Backend)

echo 🚀 Starting Credit Risk Assessment System (Development Mode)...

REM Start backend in one window
start cmd /k "cd %~dp0 && python simple_backend.py"

REM Start frontend in another window
start cmd /k "cd %~dp0\src\dashboard && npx vite"

echo.
echo ✅ Started development servers!
echo.
echo 🌐 Services will be available at:
echo   - API Backend: http://localhost:8000
echo   - API Documentation: http://localhost:8000/docs
echo   - Dashboard: http://localhost:5173 (or http://localhost:3001 if port 5173 is in use)
echo.
echo Note: If the default port is in use, Vite will automatically use the next available port.
echo Check the terminal output for the exact frontend URL.
echo.
echo 🛑 To stop: Close the terminal windows or press Ctrl+C in each window
echo.
