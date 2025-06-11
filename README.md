# AINS - AI Anti-Scam & Fact-Checking PWA

![AINS Logo](https://via.placeholder.com/150x50/1e40af/ffffff?text=AINS)

A comprehensive Progressive Web App (PWA) for AI-powered fact-checking and scam detection, built with SvelteKit frontend and FastAPI backend, designed for Azure deployment.

## 🚀 Features

### Core Functionality

- **Multi-Modal Input**: Text, image, and audio fact-checking
- **AI-Powered Analysis**: Multiple AI models for consensus-based verification
- **Offline-First**: PWA capabilities for offline usage
- **Real-Time Processing**: Concurrent model execution for fast results
- **Caching**: Redis-based caching for improved performance

### Technical Features

- **Progressive Web App**: Installable mobile app experience
- **Responsive Design**: Optimized for mobile and desktop
- **TypeScript**: Full type safety across the stack
- **Docker Support**: Containerized development and deployment
- **CI/CD Pipeline**: Automated testing and Azure deployment
- **Security Scanning**: Automated vulnerability detection
- **Monitoring**: Health checks and usage analytics

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SvelteKit     │    │    FastAPI      │    │    Azure        │
│     (PWA)       │◄──►│   (Backend)     │◄──►│   (Cloud)       │
│                 │    │                 │    │                 │
│ • Offline-first │    │ • AI Models     │    │ • Storage       │
│ • TypeScript    │    │ • Caching       │    │ • Container     │
│ • Capacitor     │    │ • Rate Limiting │    │ • Static Apps   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### AI Models Used

- **NLI (Natural Language Inference)**: RoBERTa-based model for claim verification
- **SBERT**: Sentence transformers for semantic similarity
- **ClaimBuster**: Professional fact-checking API
- **Google Fact Check**: Google's fact-checking tools API

## 📁 Project Structure

```
Hackathon-AINS/
├── frontend/                 # SvelteKit PWA
│   ├── src/
│   │   ├── lib/
│   │   │   ├── services/     # API and storage services
│   │   │   └── types.ts      # TypeScript definitions
│   │   ├── routes/           # SvelteKit routes
│   │   └── app.html          # Main HTML template
│   ├── static/              # Static assets
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.ts        # Vite configuration
│   ├── svelte.config.js      # Svelte configuration
│   ├── tailwind.config.ts    # Tailwind CSS config
│   ├── capacitor.config.ts   # Mobile app config
│   └── Dockerfile            # Frontend container
├── apis/                     # FastAPI Backend
│   ├── models/               # AI model implementations
│   │   ├── NLI/             # Natural Language Inference
│   │   ├── SBERT/           # Sentence transformers
│   │   ├── ClaimBuster/     # ClaimBuster integration
│   │   ├── Google/          # Google Fact Check API
│   │   └── Explainer/       # Result explanation
│   ├── converters/          # Media-to-text converters
│   ├── web_searcher/        # Web search functionality
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend container
│   └── compose.yaml         # Docker Compose config
├── .github/
│   └── workflows/           # CI/CD pipelines
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🛠️ Development Setup

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.10+
- **Docker** and Docker Compose
- **Git**

### Backend Setup

1. **Navigate to backend directory**

   ```cmd
   cd apis
   ```

2. **Create virtual environment**

   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```cmd
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```cmd
   copy ..\.env.example .env
   ```

   Edit `.env` and add your API keys:

   ```env
   CLAIMBUSTER_API_KEY=your_key_here
   GOOGLE_API_KEY=your_key_here
   ```

5. **Download language models**

   ```cmd
   python -c "import spacy; spacy.cli.download('en_core_web_sm')"
   ```

6. **Run the backend**
   ```cmd
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**

   ```cmd
   cd frontend
   ```

2. **Install dependencies**

   ```cmd
   npm install
   ```

3. **Set up environment variables**

   ```cmd
   copy .env.example .env.local
   ```

4. **Run the development server**
   ```cmd
   npm run dev
   ```

### Docker Setup (Recommended)

1. **Clone the repository**

   ```cmd
   git clone <repository-url>
   cd Hackathon-AINS
   ```

2. **Set up environment variables**

   ```cmd
   copy .env.example .env
   ```

3. **Start all services**
   ```cmd
   cd apis
   docker-compose up --build
   ```

This will start:

- **Backend API**: http://localhost:8000
- **Frontend PWA**: http://localhost:3000
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

## 📱 Mobile App Development

### Android Setup

```cmd
cd frontend
npm run build
npx cap add android
npx cap sync android
npx cap open android
```

### iOS Setup

```cmd
cd frontend
npm run build
npx cap add ios
npx cap sync ios
npx cap open ios
```

## 🚀 Deployment

### Azure Deployment

#### Prerequisites

- Azure CLI installed
- Azure subscription
- GitHub repository

#### Automatic Deployment

The project includes GitHub Actions workflows for automatic deployment:

1. **Fork the repository** to your GitHub account

2. **Set up Azure resources**:

   ```cmd
   az group create --name ains-rg --location eastus
   az acr create --resource-group ains-rg --name ainsregistry --sku Basic
   ```

3. **Configure GitHub Secrets**:

   - `AZURE_CREDENTIALS`: Service principal credentials
   - `AZURE_RESOURCE_GROUP`: Resource group name
   - `AZURE_STATIC_WEB_APPS_API_TOKEN`: Static Web Apps token
   - `CLAIMBUSTER_API_KEY`: ClaimBuster API key
   - `GOOGLE_API_KEY`: Google API key
   - `SECRET_KEY`: Application secret key

4. **Push to main branch** to trigger deployment

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```env
# API Configuration
FASTAPI_ENV=development
API_HOST=0.0.0.0
API_PORT=8000

# External APIs
CLAIMBUSTER_API_KEY=your_api_key
GOOGLE_API_KEY=your_api_key

# Caching
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_secret_key
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env.local)

```env
# API URL
VITE_API_URL=http://localhost:8000

# Features
VITE_ENABLE_OFFLINE_MODE=true
VITE_ENABLE_CAMERA=true
```

## 🧪 Testing

### Backend Tests

```cmd
cd apis
pytest --cov=. --cov-report=html
```

### Frontend Tests

```cmd
cd frontend
npm run test:unit
```

## 📊 Monitoring

### Health Checks

- **Backend**: http://localhost:8000/health
- **Frontend**: http://localhost:3000/health

### Metrics

- **API Usage**: Available at `/stats` endpoint
- **Performance**: Built-in timing metrics
- **Error Tracking**: Structured logging

## 🔒 Security

### Implemented Security Measures

- **CORS Configuration**: Restricted origins
- **Rate Limiting**: API request throttling
- **Input Validation**: Request sanitization
- **Security Headers**: XSS and CSRF protection
- **Container Security**: Non-root user execution
- **Secret Management**: Environment-based configuration

## 📚 API Documentation

### Main Endpoints

#### POST /classify

Analyze a statement for fact-checking

```json
{
  "prompt": "The earth is flat",
  "files": ["optional_files"]
}
```

Response:

```json
{
  "verdict": "MYTH",
  "confidence": 85.2,
  "explanation": "Scientific evidence contradicts this claim",
  "sources": ["source1", "source2"],
  "models_used": ["NLI", "SBERT", "Google"],
  "processing_time": 2.1
}
```

#### GET /health

System health check

```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "services": {
    "redis": "healthy",
    "ai_models": "healthy"
  }
}
```

## 🐛 Troubleshooting

### Common Issues

#### Backend Issues

- **Import errors**: Ensure all Python dependencies are installed
- **Model loading failures**: Check available disk space and memory
- **API key errors**: Verify environment variables are set correctly

#### Frontend Issues

- **Build failures**: Clear node_modules and reinstall dependencies
- **PWA not installing**: Check HTTPS and manifest configuration
- **API connection issues**: Verify CORS settings and network connectivity

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Hugging Face**: For transformer models
- **ClaimBuster**: For fact-checking API
- **Google**: For fact-check tools API
- **DuckDuckGo**: For search functionality
- **SvelteKit**: For the amazing frontend framework
- **FastAPI**: For the excellent backend framework

---

**Built with ❤️ for Hackathon**
