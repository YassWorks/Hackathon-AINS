# AINS Docker Setup

This repository contains a complete Docker setup for the AINS (AI Anti-Scam) project, including:

- FastAPI backend with AI models
- PostgreSQL database
- Redis cache
- Simple PWA frontend for testing

## Quick Start

### Prerequisites

- Docker Desktop installed and running
- Git (for cloning the repository)

### Option 1: Use the Startup Script (Windows)

```cmd
start-docker.bat
```

### Option 2: Manual Docker Commands

```cmd
cd apis
docker-compose up --build
```

## Services

After starting, the following services will be available:

| Service      | URL                        | Description                    |
| ------------ | -------------------------- | ------------------------------ |
| AINS API     | http://localhost:8000      | FastAPI backend with AI models |
| API Docs     | http://localhost:8000/docs | Interactive API documentation  |
| PWA Frontend | http://localhost:8080      | Simple test frontend           |
| PostgreSQL   | localhost:5432             | Database (internal)            |
| Redis        | localhost:6379             | Cache (internal)               |

## Testing the API

### Using the PWA Frontend

1. Open http://localhost:8080 in your browser
2. Enter a statement to fact-check
3. Optionally upload images or audio files
4. Click "Analyze Statement"

### Using curl

```bash
# Simple text analysis
curl -X POST "http://localhost:8000/classify" \
  -F "prompt=The Earth is flat"

# With file upload
curl -X POST "http://localhost:8000/classify" \
  -F "prompt=Check this image for misinformation" \
  -F "files=@image.jpg"
```

### Using the API Documentation

Visit http://localhost:8000/docs for interactive API testing.

## Environment Variables

Create a `.env` file in the `apis` directory with:

```env
# API Keys (optional but recommended)
CLAIMBUSTER_API_KEY=your_claimbuster_api_key
GOOGLE_API_KEY=your_google_api_key

# Database (uses Docker defaults if not specified)
DATABASE_URL=postgresql://ains_user:ains_password@postgres:5432/ains_db

# Redis (uses Docker defaults if not specified)
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production

# CORS (add your frontend URLs)
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

## Development

### Viewing Logs

```cmd
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs frontend
```

### Rebuilding Services

```cmd
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build api
```

### Stopping Services

```cmd
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## PWA Features

The test frontend includes:

- ✅ **Progressive Web App** - Installable on mobile/desktop
- ✅ **Offline Support** - Basic caching with service worker
- ✅ **Responsive Design** - Works on all screen sizes
- ✅ **File Upload** - Drag & drop support for images/audio
- ✅ **Real-time Results** - Live fact-checking results
- ✅ **Modern UI** - Clean, intuitive interface

### Installing the PWA

1. Open http://localhost:8080 in Chrome/Edge
2. Look for the install prompt or click the install button
3. The app will be added to your home screen/start menu

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PWA Frontend  │    │   AINS API      │    │   AI Models     │
│   (Port 8080)   │────│   (Port 8000)   │────│   (Integrated)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                          │
                              │                          │
                       ┌─────────────┐          ┌─────────────┐
                       │ PostgreSQL  │          │    Redis    │
                       │ (Port 5432) │          │ (Port 6379) │
                       └─────────────┘          └─────────────┘
```

## Troubleshooting

### Common Issues

1. **Port already in use**

   ```
   Error: Port 8000 is already in use
   ```

   Solution: Stop other services using these ports or change ports in docker-compose.yml

2. **Docker not running**

   ```
   Error: Cannot connect to Docker daemon
   ```

   Solution: Start Docker Desktop

3. **API connection failed**
   ```
   Cannot connect to AINS API
   ```
   Solution: Wait for all services to start (check `docker-compose logs api`)

### Health Checks

- API Health: http://localhost:8000/health
- Database: `docker-compose exec postgres pg_isready`
- Redis: `docker-compose exec redis redis-cli ping`

## Contributing

1. Make changes to the code
2. Test with Docker: `docker-compose up --build`
3. Submit a pull request

## License

MIT License - see LICENSE file for details.
