@echo off
echo 🚀 AINS Development Setup Starting...

REM Check prerequisites
echo 📋 Checking prerequisites...

REM Check Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

REM Check Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.10+ first.
    exit /b 1
)

REM Check Docker
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

echo ✅ Prerequisites check passed!

REM Setup backend
echo 🐍 Setting up backend...
cd apis

REM Create virtual environment
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

REM Download spaCy model
python -c "import spacy; spacy.cli.download('en_core_web_sm')"

echo ✅ Backend setup complete!

REM Setup frontend
echo 🌐 Setting up frontend...
cd ..\frontend

REM Install dependencies
npm install

echo ✅ Frontend setup complete!

REM Setup environment files
echo ⚙️ Setting up environment files...
cd ..

if not exist ".env" (
    copy .env.example .env
    echo 📝 Created .env file. Please edit it with your API keys.
)

if not exist "frontend\.env.local" (
    copy frontend\.env.example frontend\.env.local
    echo 📝 Created frontend\.env.local file.
)

echo 🎉 Setup complete!
echo.
echo 📚 Quick Start:
echo   1. Edit .env files with your API keys
echo   2. Start with Docker: cd apis ^&^& docker-compose up
echo   3. Or start manually:
echo      - Backend: cd apis ^&^& venv\Scripts\activate ^&^& uvicorn main:app --reload
echo      - Frontend: cd frontend ^&^& npm run dev
echo.
echo 🌐 URLs:
echo   - Frontend: http://localhost:3000
echo   - Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs

pause
