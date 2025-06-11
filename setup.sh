#!/bin/bash

# AINS Development Setup Script

echo "🚀 AINS Development Setup Starting..."

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Setup backend
echo "🐍 Setting up backend..."
cd apis

# Create virtual environment
if [ ! -d "venv" ]; then
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Download spaCy model
python -c "import spacy; spacy.cli.download('en_core_web_sm')"

echo "✅ Backend setup complete!"

# Setup frontend
echo "🌐 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend setup complete!"

# Setup environment files
echo "⚙️ Setting up environment files..."
cd ..

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📝 Created .env file. Please edit it with your API keys."
fi

if [ ! -f "frontend/.env.local" ]; then
    cp frontend/.env.example frontend/.env.local
    echo "📝 Created frontend/.env.local file."
fi

echo "🎉 Setup complete!"
echo ""
echo "📚 Quick Start:"
echo "  1. Edit .env files with your API keys"
echo "  2. Start with Docker: cd apis && docker-compose up"
echo "  3. Or start manually:"
echo "     - Backend: cd apis && source venv/bin/activate && uvicorn main:app --reload"
echo "     - Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 URLs:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
