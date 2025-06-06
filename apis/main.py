from fastapi import FastAPI
from helpers.utils import is_claim
from models.NLI.model import avg_predict
from models.LoReN.model import evaluate_claim
from web_searcher.app import search_topic

app = FastAPI(title="ANTI-SCAM API")

@app.post("/classify")
def verify_claim(statement: str):
    
    if is_claim(statement) != "claim":
        return {"Error": "The statement is not a claim, it's more like a subjective opinion. Please provide a valid claim."}

    sources = search_topic(statement, num_paragraphs=20)

    result1 = avg_predict(statement, sources)
    result2 = evaluate_claim(statement)

    # Voting logic
    labels = ["FACT", "MYTH", "SCAM"]
    probs = [0, 0, 0]

    # NLI
    if result1 != "UNCERTAIN":
        probs[labels.index(result1)] += 1

    # LoReN
    probs[labels.index(result2)] += 1

    return {"Success": probs[probs.index(max(probs))]}