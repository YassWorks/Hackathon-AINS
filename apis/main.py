from fastapi import FastAPI
from helpers.utils import is_claim
from models.NLI.model import avg_predict
from models.LoReN.model import evaluate_claim
from web_searcher.app import search_topic
from models.ClaimBuster.model import verify_claim_claimbuster
from models.SBERT.model import sbert_predict
from models.Google.model import verify_claim_google_factcheck

app = FastAPI(title="ANTI-SCAM API")

@app.post("/classify")
def verify_claim(statement: str):
    
    if is_claim(statement) != "claim":
        return {"Error": "The statement is not a claim, it's more like a subjective opinion. Please provide a valid claim."}

    sources = search_topic(statement, num_paragraphs=20)

    result1 = avg_predict(statement, sources)
    result2 = evaluate_claim(statement)
    result3 = verify_claim_claimbuster(statement)
    result4 = sbert_predict(statement, sources)
    result5 = verify_claim_google_factcheck(statement, verbose=False)

    # Voting logic
    labels = ["FACT", "MYTH", "SCAM"]
    probs = [0, 0, 0]

    # NLI
    if result1 != "UNCERTAIN":
        probs[labels.index(result1)] += 1

    # LoReN
    probs[labels.index(result2)] += 1
    
    # ClaimBuster
    probs[labels.index(result3)] += 1

    # SBERT
    if result4 != "UNKNOWN":
        probs[labels.index(result4)] += 1

    # Google Fact Check API
    if result5 != "UNKNOWN":
        probs[labels.index(result5)] += 1

    return {"Success": labels[probs[probs.index(max(probs))]]}

l = verify_claim("The earth is flat.")
print(f"The claim 'The earth is flat.' is classified as: {l}")