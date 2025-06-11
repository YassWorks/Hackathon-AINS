# Makefile for AINS Project

.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build test clean docker-up docker-down

# Default target
help:
	@echo "AINS Project Commands:"
	@echo "  install          - Install all dependencies"
	@echo "  install-backend  - Install backend dependencies"
	@echo "  install-frontend - Install frontend dependencies"
	@echo "  dev              - Start development servers"
	@echo "  dev-backend      - Start backend development server"
	@echo "  dev-frontend     - Start frontend development server"
	@echo "  build            - Build all projects"
	@echo "  test             - Run all tests"
	@echo "  clean            - Clean build artifacts"
	@echo "  docker-up        - Start with Docker Compose"
	@echo "  docker-down      - Stop Docker Compose"

# Installation
install: install-backend install-frontend

install-backend:
	cd apis && python -m venv venv
	cd apis && venv/Scripts/activate && pip install -r requirements.txt
	cd apis && venv/Scripts/activate && python -c "import spacy; spacy.cli.download('en_core_web_sm')"

install-frontend:
	cd frontend && npm install

# Development
dev: dev-backend dev-frontend

dev-backend:
	cd apis && venv/Scripts/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# Building
build:
	cd frontend && npm run build

# Testing
test:
	cd apis && venv/Scripts/activate && pytest
	cd frontend && npm run test:unit

# Cleanup
clean:
	cd frontend && rm -rf node_modules build .svelte-kit
	cd apis && rm -rf __pycache__ .pytest_cache .coverage

# Docker
docker-up:
	cd apis && docker-compose up --build

docker-down:
	cd apis && docker-compose down

# Environment setup
setup-env:
	cp .env.example .env
	cp frontend/.env.example frontend/.env.local
	@echo "Please edit .env files with your API keys"
