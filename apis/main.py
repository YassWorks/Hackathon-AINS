from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import tempfile
import os
from helpers.utils import is_claim
from models.NLI.model import avg_predict
from models.LoReN.model import evaluate_claim
from web_searcher.app import search_topic
from models.ClaimBuster.model import verify_claim_claimbuster
from models.SBERT.model import sbert_predict
from models.Google.model import verify_claim_google_factcheck
import threading
from dotenv import load_dotenv


load_dotenv()


CLAIM_BUSTER_API_KEY = os.getenv("CLAIMBUSTER_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


app = FastAPI(title="ANTI-SCAM API")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add this data model
class StatementRequest(BaseModel):
    statement: str


@app.post("/classify")
async def verify_claim(
    prompt: str = Form(...),
    files: List[UploadFile] = File(None)
):
    try:
        full_statement = prompt
        
        # Check if it's a claim
        # if is_claim(full_statement) != "claim":
        #     return {"Error": "The statement is not a claim, it's more like a subjective opinion. Please provide a valid claim."}

        # Search for sources
        sources = search_topic(full_statement, num_paragraphs=20)

        # Get predictions from different models
        result1, result2, result3, result4, result5 = None, None, None, None, None

        def run_avg_predict():
            nonlocal result1
            result1 = avg_predict(full_statement, sources)

        def run_evaluate_claim():
            nonlocal result2
            result2 = evaluate_claim(full_statement, sources)

        def run_verify_claim_claimbuster():
            nonlocal result3
            result3 = verify_claim_claimbuster(full_statement, CLAIM_BUSTER_API_KEY)

        def run_sbert_predict():
            nonlocal result4
            result4 = sbert_predict(full_statement, sources)

        def run_verify_claim_google_factcheck():
            nonlocal result5
            result5 = verify_claim_google_factcheck(full_statement, GOOGLE_API_KEY)

        # Create threads
        threads = [
            threading.Thread(target=run_avg_predict),
            threading.Thread(target=run_evaluate_claim),
            threading.Thread(target=run_verify_claim_claimbuster),
            threading.Thread(target=run_sbert_predict),
            threading.Thread(target=run_verify_claim_google_factcheck),
        ]

        # Start threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Voting logic
        labels = ["FACT", "MYTH", "SCAM"]
        probs = [0, 0, 0]

        # NLI
        if result1 != "UNCERTAIN":
            probs[labels.index(result1)] += 1

        # LoReN
        # if result2 != "UNKNOWN":
        #     probs[labels.index(result2)] += 1
        
        # ClaimBuster
        if result3 != "UNCERTAIN":
            probs[labels.index(result3)] += 1
        
        if result4 != "UNKNOWN":
            probs[labels.index(result4)] += 1
        
        if result5 != "UNKNOWN":
            probs[labels.index(result5)] += 1

        print(f"Results: {result1}, {result2}, {result3}, {result4}, {result5}")
        final_verdict = labels[probs.index(max(probs))]
        return {"Success": final_verdict}
        
    except Exception as e:
        return {"Error": f"An error occurred: {str(e)}"}


# l = verify_claim("The earth is flat.")
# print(f"The claim 'The earth is flat.' is classified as: {l}")