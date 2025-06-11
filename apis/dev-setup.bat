@echo off
REM Development setup script for uv + Docker on Windows

echo 🚀 Setting up AINS development environment with uv...

REM Check if we're in the correct directory
if not exist "pyproject.toml" (
    echo ❌ Error: pyproject.toml not found. Please run this from the apis directory.
    exit /b 1
)

echo 📦 Building development Docker image...
docker build -f Dockerfile.dev -t ains-dev .

echo 🔧 Starting development services...
docker-compose --profile dev up --build -d

echo ✅ Development environment ready!
echo 🌐 API available at: http://localhost:8001
echo 🔄 Hot reload enabled for development
echo.
echo To watch for changes, run:
echo docker compose watch
echo.
echo To stop services:
echo docker-compose --profile dev down

pause
