import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

def verify_claim_claimbuster(input_claim, verbose=False):
    
    # defining the URL and the payload
    api_endpoint = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
    request_headers = {"x-api-key": api_key}
    payload = {"input_text": input_claim}

    api_response = requests.post(url=api_endpoint, json=payload, headers=request_headers)

    result = api_response.json()

    if verbose:
        print("[INFO]: API Response:")
        print(json.dumps(result, indent=4))
    
    score = result.get("results", None)[0]["score"]

    # Defining rules for the score
    
    # If the score is greater than 0.7, we consider it a FACT.
    # If the score is between 0.4 and 0.7, we consider it a MYTH.
    # If the score is less than 0.4, we consider it a SCAM.

    print(f"The score is: {score}")
    if score > 0.7:
        classification = "FACT"
    elif 0.4 <= score <= 0.7:
        classification = "MYTH"
    elif score < 0.4:
        classification = "SCAM"
        
    return classification


if __name__ == "__main__":
    input_claim = "The Earth is flat."
    classification = verify_claim_claimbuster(input_claim, verbose=True)
    print(f"The claim '{input_claim}' is classified as: {classification}")