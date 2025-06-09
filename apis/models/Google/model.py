import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

def verify_claim_google_factcheck(claim, verbose=False):
    url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
    params = {
        "query": claim,
        "key": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if verbose:
        import json
        print("[INFO]: API Response:")
        print(json.dumps(data, indent=4))

    verdicts = []
    claims = data.get("claims", [])
    for claim_item in claims:
        for review in claim_item.get("claimReview", []):
            rating = review.get("textualRating", "").upper()
            verdicts.append(rating)

    if not verdicts:
        print("No fact-check verdicts found.")
        return "UNKNOWN"

    # Simple scoring logic
    def map_score(rating):
        if "FALSE" in rating or "PANTS ON FIRE" in rating:
            return -1
        elif "TRUE" in rating:
            return 1
        elif "PARTLY" in rating or "MIXED" in rating:
            return 0.5
        elif "MISLEADING" in rating:
            return -0.5
        return 0

    scores = [map_score(v) for v in verdicts]
    avg_score = sum(scores) / len(scores)

    if avg_score >= 0.5:
        classification = "FACT"
    elif 0 < avg_score < 0.5:
        classification = "MYTH"
    else:
        classification = "SCAM"

    print(f"The average score is: {avg_score}")
    return classification

'''
if __name__ == "__main__":
    test_claim = "5G causes cancer."
    result = verify_claim_google_factcheck(test_claim, verbose=True)
    print(f"The claim '{test_claim}' is classified as: {result}")
'''