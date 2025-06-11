# Docker Setup with UV Package Manager

This project uses [uv](https://docs.astral.sh/uv/) as the Python package manager for faster dependency resolution and installation.

## 🚀 Quick Start

### Production Build

```bash
# Build and run production containers
docker-compose up --build

# API will be available at http://localhost:8000
```

### Development Setup

```bash
# On Windows
dev-setup.bat

# On Linux/Mac
./dev-setup.sh

# Or manually:
docker-compose --profile dev up --build

# API will be available at http://localhost:8001 with hot reload
```

### Development with Watch Mode

For the best development experience with automatic rebuilds:

```bash
docker compose watch
```

This will:

- Sync code changes automatically to the container
- Restart the server on file changes
- Rebuild the image when `pyproject.toml` changes

## 📁 Docker Files

- **`Dockerfile`** - Production build with optimized layers
- **`Dockerfile.dev`** - Development build with hot reload
- **`docker-compose.yml`** - Multi-service setup with profiles
- **`.dockerignore`** - Optimized for uv and development

## 🔧 uv Benefits

- **Faster installs**: 10-100x faster than pip
- **Better caching**: Efficient dependency caching across builds
- **Lock files**: Deterministic dependency resolution with `uv.lock`
- **Modern tooling**: Built-in project management

## 🛠️ Development Commands

```bash
# Start development environment
docker-compose --profile dev up -d

# View logs
docker-compose --profile dev logs -f api-dev

# Execute commands in dev container
docker-compose --profile dev exec api-dev uv run python

# Run tests in container
docker-compose --profile dev exec api-dev uv run pytest

# Stop development environment
docker-compose --profile dev down
```

## 🏗️ Build Optimizations

The Dockerfiles use several optimizations:

1. **Multi-stage caching**: Dependencies installed in separate layer
2. **uv cache mounts**: Shared cache across builds
3. **Bytecode compilation**: Faster startup in production
4. **Non-root user**: Security best practices
5. **Health checks**: Container health monitoring

## 📋 Environment Variables

### Production

- `UV_COMPILE_BYTECODE=1` - Compile Python bytecode
- `UV_LINK_MODE=copy` - Use copy mode for Docker

### Development

- `UV_COMPILE_BYTECODE=0` - Skip bytecode compilation for faster rebuilds
- Hot reload enabled via `--reload` flag

## 🐛 Troubleshooting

### Build Issues

```bash
# Clear Docker cache
docker builder prune

# Force rebuild without cache
docker-compose build --no-cache
```

### Development Issues

```bash
# Restart dev container
docker-compose --profile dev restart api-dev

# View container logs
docker-compose --profile dev logs api-dev
```

### Dependency Issues

```bash
# Update lock file locally first
uv lock

# Then rebuild containers
docker-compose build
```

## 📚 References

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv Docker Guide](https://docs.astral.sh/uv/guides/integration/docker/)
- [Docker Compose Watch](https://docs.docker.com/compose/file-watch/)
