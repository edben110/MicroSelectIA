@echo off
echo ========================================
echo   MicroSelectIA - Docker Deployment
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running
    echo Please start Docker Desktop and try again
    pause
    exit /b 1
)

REM Build and start containers
echo Building and starting containers...
docker-compose up --build -d

if errorlevel 1 (
    echo ERROR: Failed to start containers
    pause
    exit /b 1
)

echo.
echo ========================================
echo   MicroSelectIA started successfully!
echo ========================================
echo.
echo API: http://localhost:8000
echo Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.
echo To view logs: docker-compose logs -f microselectia
echo To stop: docker-compose down
echo.

pause
