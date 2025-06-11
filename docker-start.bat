@echo off
REM Docker Management Script for AINS API-First Development

set ENV=%1
if "%ENV%"=="" set ENV=dev

echo AINS API Docker Environment Manager
echo ===================================

if "%ENV%"=="dev" (
    echo Starting API development environment...
    cd apis
    docker-compose --env-file ../.env.docker up --build -d
    echo.
    echo API Services started:
    echo   - API: http://localhost:8000
    echo   - API Docs: http://localhost:8000/docs
    echo   - API Health: http://localhost:8000/health
    echo   - Redis: localhost:6379
    echo   - PostgreSQL: localhost:5432
    echo.
    echo Note: Frontend development should be done separately
    echo Audio processing is disabled for Docker compatibility
) else if "%ENV%"=="prod" (
    echo Starting production API environment...
    cd apis
    docker-compose --env-file ../.env.production up --build -d
    echo.
    echo Production API services started
) else if "%ENV%"=="stop" (
    echo Stopping all API services...
    cd apis
    docker-compose down
    echo API services stopped.
) else if "%ENV%"=="clean" (
    echo Cleaning up Docker resources...
    cd apis
    docker-compose down -v --remove-orphans
    docker system prune -f
    echo Cleanup completed.
) else if "%ENV%"=="logs" (
    echo Showing API container logs...
    cd apis
    docker-compose logs -f
) else (
    echo.
    echo Usage: %0 [dev^|prod^|stop^|clean^|logs]
    echo.
    echo   dev    - Start API development environment [default]
    echo   prod   - Start API production environment
    echo   stop   - Stop all API services
    echo   clean  - Clean up all Docker resources
    echo   logs   - Show API container logs
    echo.
    echo Examples:
    echo   %0 dev     - Start API development environment
    echo   %0 prod    - Start API production environment
    echo   %0 stop    - Stop all API services
    echo.
    echo Frontend Development:
    echo   Use "npm run dev" in the frontend folder for local frontend development
    echo   The API will be available at http://localhost:8000
)

if "%ENV%" NEQ "help" if "%ENV%" NEQ "stop" if "%ENV%" NEQ "clean" if "%ENV%" NEQ "logs" (
    echo.
    echo To stop API services: %0 stop
    echo To view logs: %0 logs
    echo To clean up: %0 clean
)
