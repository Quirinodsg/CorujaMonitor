@echo off
echo ========================================
echo Coruja Monitor - Setup Script
echo ========================================
echo.

REM Check for Docker
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows
    echo https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [1/5] Checking Docker...
echo Docker found!
echo.

echo [2/5] Creating environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it with your configuration.
    echo.
    echo IMPORTANT: Set your OpenAI API key in .env file!
    echo.
    pause
) else (
    echo .env file already exists.
)
echo.

echo [3/5] Building Docker images...
docker compose build
if %errorLevel% neq 0 (
    echo ERROR: Failed to build Docker images
    pause
    exit /b 1
)
echo.

echo [4/5] Starting services...
docker compose up -d
if %errorLevel% neq 0 (
    echo ERROR: Failed to start services
    pause
    exit /b 1
)
echo.

echo [5/5] Waiting for services to be ready...
timeout /t 10 /nobreak >nul
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Services are running:
echo - Frontend: http://localhost:3000
echo - API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - AI Agent: http://localhost:8001
echo.
echo Next steps:
echo 1. Create admin user (see README.md)
echo 2. Login to dashboard
echo 3. Create a probe
echo 4. Install probe on client machines
echo.
echo To view logs: docker compose logs -f
echo To stop: docker compose down
echo.
pause
