from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional
import os
import time
import logging
from contextlib import asynccontextmanager
from models.NLI.model import avg_predict
from web_searcher.app import search_topic
from models.ClaimBuster.model import verify_claim_claimbuster
from models.SBERT.model import sbert_predict
from models.Google.model import verify_claim_google_factcheck
import threading
from dotenv import load_dotenv
import redis
import json
from datetime import datetime, timedelta

load_dotenv()

# Configuration
CLAIM_BUSTER_API_KEY = os.getenv("CLAIMBUSTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# Initialize Redis for caching
try:
    redis_client = redis.from_url(REDIS_URL)
except Exception as e:
    logging.warning(f"Redis connection failed: {e}")
    redis_client = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AINS API...")
    yield
    # Shutdown
    logger.info("Shutting down AINS API...")

app = FastAPI(
    title="AINS API",
    description="AI-powered anti-scam and fact-checking API",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
security = HTTPBearer()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure this properly in production
)

class StatementRequest(BaseModel):
    statement: str

class ClaimResponse(BaseModel):
    verdict: str
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    sources: Optional[List[str]] = None
    models_used: Optional[List[str]] = None
    processing_time: Optional[float] = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: dict

def get_cache_key(statement: str, files_hash: str = "") -> str:
    """Generate cache key for the claim"""
    import hashlib
    content = f"{statement}:{files_hash}"
    return f"claim:{hashlib.md5(content.encode()).hexdigest()}"

def cache_result(key: str, result: dict, ttl: int = 3600):
    """Cache the result in Redis"""
    if redis_client:
        try:
            redis_client.setex(key, ttl, json.dumps(result))
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")

def get_cached_result(key: str) -> Optional[dict]:
    """Get cached result from Redis"""
    if redis_client:
        try:
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Failed to get cached result: {e}")
    return None

async def log_api_usage(endpoint: str, processing_time: float, status: str):
    """Log API usage for monitoring"""
    logger.info(f"API Usage - Endpoint: {endpoint}, Time: {processing_time:.2f}s, Status: {status}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {
        "redis": "healthy" if redis_client and redis_client.ping() else "unhealthy",
        "ai_models": "healthy"  # Add model health checks here
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        services=services
    )

@app.post("/classify", response_model=ClaimResponse)
async def verify_claim(
    background_tasks: BackgroundTasks,
    prompt: str = Form(...),
    files: List[UploadFile] = File(None)
):
    start_time = time.time()
    
    try:
        # Input validation
        if not prompt.strip():
            raise HTTPException(status_code=400, detail="Statement cannot be empty")
        
        if len(prompt) > 5000:
            raise HTTPException(status_code=400, detail="Statement too long (max 5000 characters)")

        full_statement = prompt  # + context from the files (will add later)
        
        # Generate cache key
        files_hash = ""
        if files:
            files_hash = str(hash(tuple(f.filename for f in files if f.filename)))
        
        cache_key = get_cache_key(full_statement, files_hash)
        
        # Check cache first
        cached_result = get_cached_result(cache_key)
        if cached_result:
            processing_time = time.time() - start_time
            background_tasks.add_task(log_api_usage, "/classify", processing_time, "cached")
            return ClaimResponse(**cached_result, processing_time=processing_time)

        # Search for sources
        sources = search_topic(full_statement, num_paragraphs=20)

        # Get predictions from different models
        result1, result2, result3, result4 = None, None, None, None

        def run_avg_predict():
            nonlocal result1
            try:
                result1 = avg_predict(full_statement, sources)
            except Exception as e:
                logger.error(f"NLI model error: {e}")
                result1 = "UNCERTAIN"

        def run_verify_claim_claimbuster():
            nonlocal result2
            try:
                result2 = verify_claim_claimbuster(full_statement, CLAIM_BUSTER_API_KEY)
            except Exception as e:
                logger.error(f"ClaimBuster error: {e}")
                result2 = "UNCERTAIN"

        def run_sbert_predict():
            nonlocal result3
            try:
                result3 = sbert_predict(full_statement, sources)
            except Exception as e:
                logger.error(f"SBERT error: {e}")
                result3 = "UNKNOWN"

        def run_verify_claim_google_factcheck():
            nonlocal result4
            try:
                result4 = verify_claim_google_factcheck(full_statement, GOOGLE_API_KEY)
            except Exception as e:
                logger.error(f"Google Fact Check error: {e}")
                result4 = "UNKNOWN"

        # Create threads with timeout
        threads = [
            threading.Thread(target=run_avg_predict),
            threading.Thread(target=run_verify_claim_claimbuster),
            threading.Thread(target=run_sbert_predict),
            threading.Thread(target=run_verify_claim_google_factcheck),
        ]

        # Start threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete with timeout
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per thread

        # Voting logic
        labels = ["FACT", "MYTH", "SCAM"]
        votes = {label: 0 for label in labels}
        models_used = []

        # Count votes
        if result1 and result1 in labels:
            votes[result1] += 1
            models_used.append("NLI")
        
        if result2 and result2 in labels:
            votes[result2] += 1
            models_used.append("ClaimBuster")
        
        if result3 and result3 in labels:
            votes[result3] += 1
            models_used.append("SBERT")
        
        if result4 and result4 in labels:
            votes[result4] += 1
            models_used.append("Google")

        logger.info(f"Model results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}")
        
        # Determine final verdict
        if not any(votes.values()):
            final_verdict = "UNKNOWN"
            confidence = 0.0
        else:
            final_verdict = max(votes.keys(), key=votes.get)
            confidence = (votes[final_verdict] / len(models_used)) * 100 if models_used else 0.0

        # Generate explanation
        explanations = {
            "FACT": "This statement appears to be factually accurate based on available evidence.",
            "MYTH": "This statement contains misleading or partially incorrect information.",
            "SCAM": "This statement shows characteristics of fraudulent content. Exercise caution.",
            "UNKNOWN": "Unable to verify this statement with available sources."
        }
        
        processing_time = time.time() - start_time
        
        response_data = {
            "verdict": final_verdict,
            "confidence": round(confidence, 2),
            "explanation": explanations.get(final_verdict, explanations["UNKNOWN"]),
            "sources": sources[:3] if sources else [],  # Limit to top 3 sources
            "models_used": models_used,
            "processing_time": round(processing_time, 2)
        }
        
        # Cache the result
        cache_result(cache_key, response_data)
        
        # Log API usage
        background_tasks.add_task(log_api_usage, "/classify", processing_time, "success")
        
        return ClaimResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Classification error: {str(e)}")
        background_tasks.add_task(log_api_usage, "/classify", processing_time, "error")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get API usage statistics"""
    try:
        if redis_client:
            # Get some basic stats from Redis
            info = redis_client.info()
            return {
                "redis_connected_clients": info.get("connected_clients", 0),
                "redis_total_commands_processed": info.get("total_commands_processed", 0),
                "cache_enabled": True
            }
        else:
            return {"cache_enabled": False}
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": "Failed to get stats"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AINS API - AI-powered anti-scam and fact-checking service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }