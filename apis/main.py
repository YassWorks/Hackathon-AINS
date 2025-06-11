from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from models.NLI.model import avg_predict
from web_searcher.app import search_topic
from models.ClaimBuster.model import verify_claim_claimbuster
from models.SBERT.model import sbert_predict
from models.Google.model import verify_claim_google_factcheck
from models.TunBERT.model import tunbert_fact_check, get_detailed_analysis
from models.LLM.groq import groq_fact_check, get_detailed_groq_analysis
import threading
from dotenv import load_dotenv


load_dotenv()


CLAIM_BUSTER_API_KEY = os.getenv("CLAIMBUSTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


app = FastAPI(title="ANTI-SCAM API")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StatementRequest(BaseModel):
    statement: str


@app.post("/classify")
async def verify_claim(
    prompt: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        full_statement = prompt # + context from the files (will add later)        # Search for sources
        sources = search_topic(full_statement, num_paragraphs=20)
        
        # Get predictions from different models
        result1, result2, result3, result4, result5, result6 = None, None, None, None, None, None

        def run_avg_predict():
            nonlocal result1
            result1 = avg_predict(full_statement, sources)

        def run_verify_claim_claimbuster():
            nonlocal result2
            result2 = verify_claim_claimbuster(full_statement, CLAIM_BUSTER_API_KEY)

        def run_sbert_predict():
            nonlocal result3
            result3 = sbert_predict(full_statement, sources)

        def run_verify_claim_google_factcheck():
            nonlocal result4
            result4 = verify_claim_google_factcheck(full_statement, GOOGLE_API_KEY)

        def run_tunbert_predict():
            nonlocal result5
            result5 = tunbert_fact_check(full_statement, sources)

        def run_groq_predict():
            nonlocal result6
            result6 = groq_fact_check(full_statement, sources)

        # Create threads
        threads = [
            threading.Thread(target=run_avg_predict),
            threading.Thread(target=run_verify_claim_claimbuster),
            threading.Thread(target=run_sbert_predict),
            threading.Thread(target=run_verify_claim_google_factcheck),
            threading.Thread(target=run_tunbert_predict),
            threading.Thread(target=run_groq_predict),
        ]

        # Start threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()        # Voting logic
        labels = ["FACT", "MYTH", "SCAM"]
        probs = [0, 0, 0]

        # NLI
        if result1 != "UNCERTAIN":
            probs[labels.index(result1)] += 1
        
        # ClaimBuster
        if result2 != "UNCERTAIN":
            probs[labels.index(result2)] += 1
        
        # SBERT
        if result3 != "UNKNOWN":
            probs[labels.index(result3)] += 1
        
        # Google Fact Check
        if result4 != "UNKNOWN":
            probs[labels.index(result4)] += 1
        
        # TunBERT
        if result5 != "UNCERTAIN":
            probs[labels.index(result5)] += 1
        
        # Groq Qwen3-32B
        if result6 != "UNCERTAIN":
            probs[labels.index(result6)] += 1

        print(f"Results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}, TunBERT={result5}, Groq={result6}")
        
        # Handle case where no model gives a confident prediction
        if max(probs) == 0:
            final_verdict = "UNCERTAIN"
        else:
            final_verdict = labels[probs.index(max(probs))]
        
        return {
            "Success": final_verdict,
            "model_results": {
                "NLI": result1,
                "ClaimBuster": result2,
                "SBERT": result3,
                "Google": result4,
                "TunBERT": result5,
                "Groq": result6
            },
            "vote_counts": dict(zip(labels, probs))
        }
        
    except Exception as e:
        return {"Error": f"An error occurred: {str(e)}"}


@app.post("/groq-analyze")
async def groq_detailed_analysis(
    prompt: str = Form(...),
    include_sources: bool = Form(True)
):
    """
    Get detailed analysis from Groq Qwen3-32B model with confidence scores and reasoning.
    """
    try:
        sources = []
        if include_sources:
            # Search for sources if requested
            sources = search_topic(prompt, num_paragraphs=10)
        
        # Get detailed analysis from Groq
        detailed_result = get_detailed_groq_analysis(prompt, sources if include_sources else None)
        
        # Also get the simple classification for compatibility
        simple_result = groq_fact_check(prompt, sources if include_sources else None)
        
        return {
            "claim": prompt,
            "simple_classification": simple_result,
            "detailed_analysis": detailed_result,
            "sources_used": len(sources) if include_sources else 0,
            "timestamp": "2025-06-11",
            "model": "Groq Qwen2.5-32B"
        }
        
    except Exception as e:
        return {"Error": f"An error occurred in Groq analysis: {str(e)}"}


@app.post("/tunbert-analyze")
async def tunbert_detailed_analysis(
    prompt: str = Form(...),
    include_sources: bool = Form(True)
):
    """
    Get detailed analysis from TunBERT model with confidence scores and source analysis.
    """
    try:
        sources = []
        if include_sources:
            # Search for sources if requested
            sources = search_topic(prompt, num_paragraphs=10)
        
        # Get detailed analysis from TunBERT
        detailed_result = get_detailed_analysis(prompt, sources if include_sources else None)
        
        # Also get the simple classification for compatibility
        simple_result = tunbert_fact_check(prompt, sources if include_sources else None)
        
        return {
            "claim": prompt,
            "simple_classification": simple_result,
            "detailed_analysis": detailed_result,
            "sources_used": len(sources) if include_sources else 0,
            "timestamp": "2025-06-11"  # You can use actual timestamp if needed
        }
        
    except Exception as e:
        return {"Error": f"An error occurred in TunBERT analysis: {str(e)}"}


@app.get("/models/status")
async def get_models_status():
    """
    Check the status of all available models including TunBERT and Groq.
    """
    try:
        models_status = {
            "NLI": "Available",
            "ClaimBuster": "Available" if CLAIM_BUSTER_API_KEY else "API Key Missing",
            "SBERT": "Available", 
            "Google": "Available" if GOOGLE_API_KEY else "API Key Missing",
            "TunBERT": "Available",
            "Groq": "Available" if GROQ_API_KEY else "API Key Missing"
        }
        
        return {
            "status": "success",
            "models": models_status,
            "total_models": len(models_status)
        }
        
    except Exception as e:
        return {"Error": f"An error occurred checking model status: {str(e)}"}


@app.get("/")
async def root():
    return {
        "message": "ANTI-SCAM API with TunBERT and Groq Qwen3-32B Fact Checkers",
        "version": "1.2.0",
        "available_endpoints": [
            "/classify - Main fact-checking endpoint with ensemble voting",
            "/tunbert-analyze - Detailed TunBERT analysis",
            "/groq-analyze - Detailed Groq Qwen3-32B analysis",
            "/models/status - Check model availability",
            "/docs - API documentation"
        ],
        "models": ["NLI", "ClaimBuster", "SBERT", "Google Fact Check", "TunBERT", "Groq Qwen2.5-32B"]
    }