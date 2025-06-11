@echo off
echo Starting AINS Docker Environment...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo Docker is running. Starting services...
echo.

REM Navigate to apis directory
cd /d "%~dp0apis"

REM Start Docker Compose
docker-compose up --build

echo.
echo Services stopped.
pause
