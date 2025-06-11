# AINS API-First Development Setup

## Overview

The AINS project has been converted to an **API-first development approach**. This means:

1. ✅ **Backend API runs in Docker** - Consistent, isolated environment
2. ✅ **Frontend developed separately** - Faster iteration, better debugging
3. ✅ **Audio processing removed** - No more Docker build issues
4. ✅ **Simplified deployment** - Focus on API stability first

## Quick Start Commands

```bash
# Start the API environment
docker-start.bat dev

# API will be available at:
# - http://localhost:8000 (API endpoints)
# - http://localhost:8000/docs (Interactive documentation)
# - http://localhost:8000/health (Health check)

# For frontend development (separate terminal):
cd frontend
npm run dev
# Frontend will connect to API at localhost:8000
```

## What's Changed

### ✅ Removed from Docker

- Frontend build process (no more npm ci errors)
- Audio processing dependencies (no more pyaudio errors)
- Frontend container and nginx complexity

### ✅ Kept in Docker

- FastAPI backend
- PostgreSQL database
- Redis caching
- All AI/ML models and processing

### ✅ Environment Files Updated

- `.env.docker` - API-focused environment variables
- `.env.production` - Production API deployment
- CORS configured for localhost frontend development

## Development Workflow

### 1. Start API Services

```bash
docker-start.bat dev
```

This starts:

- API server (with auto-reload)
- PostgreSQL database
- Redis cache

### 2. Develop Frontend Separately

```bash
cd frontend
npm install  # First time only
npm run dev
```

Frontend connects to API at `http://localhost:8000`

### 3. Test API

- **Interactive docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health
- **Alternative docs**: http://localhost:8000/redoc

## Benefits of This Approach

### 🚀 **Faster Development**

- No frontend Docker build time
- Frontend hot reload works perfectly
- API changes reflected immediately

### 🐛 **Better Debugging**

- Frontend runs in native environment
- Better browser dev tools integration
- Clearer error messages

### 🔧 **Simpler Deployment**

- API Docker images are smaller
- No frontend build dependencies in API container
- Can deploy API and frontend independently

### 🧪 **Easier Testing**

- API endpoints easily testable via docs
- Frontend can be tested with different API versions
- Unit tests run faster

## File Structure

```
apis/
├── Dockerfile              # API-only container
├── docker-compose.yml      # API services only
├── requirements.txt        # No audio dependencies
└── main.py                 # FastAPI app

frontend/
├── package.json            # Frontend dependencies
├── src/                    # Frontend source
└── (develop with npm run dev)
```

## Available Scripts

### Docker Management

- `docker-start.bat dev` - Start API development environment
- `docker-start.bat stop` - Stop all API services
- `docker-start.bat logs` - View API logs
- `docker-start.bat clean` - Clean up Docker resources

### Frontend Development

- `npm run dev` - Start frontend development server
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build

## Troubleshooting

### API Issues

- Check `docker-start.bat logs` for API errors
- Verify ports 8000, 5432, 6379 are available
- Check `.env.docker` for correct settings

### Frontend Issues

- Make sure API is running first (`docker-start.bat dev`)
- Check that `VITE_API_URL` points to `http://localhost:8000`
- Verify CORS settings allow frontend origin

### Audio Files

- Audio processing is disabled
- Users get clear error messages
- Focus on text and image processing

## Next Steps

1. ✅ **API Development**: Focus on perfecting the AI/ML endpoints
2. ✅ **Frontend Polish**: Enhance UI/UX without Docker complexity
3. ✅ **Testing**: Easy API testing via interactive docs
4. ✅ **Deployment**: Deploy API to cloud, frontend to CDN

This setup provides the best development experience while maintaining production reliability!
