import requests

def verify_claim_claimbuster(input_claim, api_key):
    
    try:
        # defining the URL and the payload
        api_endpoint = "https://idir.uta.edu/claimbuster/api/v2/score/text/"
        request_headers = {"x-api-key": api_key}
        payload = {"input_text": input_claim}

        api_response = requests.post(url=api_endpoint, json=payload, headers=request_headers)

        result = api_response.json()
        
        if "results" in result:
            score = result.get("results", None)[0]["score"]
        else:
            print("[ERROR]: Unexpected API response format.")
            return "UNCERTAIN"

        # Defining rules for the score
        
        # If the score is greater than 0.7, we consider it a FACT.
        # If the score is between 0.4 and 0.7, we consider it a MYTH.
        # If the score is less than 0.4, we consider it a SCAM.

        print(f"The score is: {score}")
        if score >= 0.5:
            classification = "FACT"
        elif 0.25 <= score < 0.5:
            classification = "MYTH"
        elif score < 0.25:
            classification = "SCAM"
            
        return classification
    
    except Exception as e:
        
        print(f"[ERROR]: An error occurred while verifying the claim using ClaimBuster: {e}")
        return "UNCERTAIN"