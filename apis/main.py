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
# from converters.converter import convert_to_text


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
        # Combine prompt with file content
        full_statement = prompt
        
        # Process uploaded files if any
        if files:
            ...
            # file_contents = []
            # for file in files:
            #     if file.filename:
            #         # Save file temporarily
            #         with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            #             content = await file.read()
            #             temp_file.write(content)
            #             temp_file_path = temp_file.name
                    
            #         try:
            #             # Convert file to text
            #             file_text = convert_to_text(temp_file_path)
            #             file_contents.append(f"File '{file.filename}': {file_text}")
            #         except Exception as e:
            #             file_contents.append(f"File '{file.filename}': Error processing - {str(e)}")
            #         finally:
            #             # Clean up temp file
            #             os.unlink(temp_file_path)
            
            # if file_contents:
            #     full_statement += "\n\nAdditional context from files:\n" + "\n".join(file_contents)
        
        # Check if it's a claim
        # if is_claim(full_statement) != "claim":
        #     return {"Error": "The statement is not a claim, it's more like a subjective opinion. Please provide a valid claim."}

        # Search for sources
        sources = search_topic(full_statement, num_paragraphs=20)

        # Get predictions from different models
        result1 = avg_predict(full_statement, sources)
        # result2 = evaluate_claim(full_statement, sources)
        result3 = verify_claim_claimbuster(full_statement)
        result4 = sbert_predict(full_statement, sources)
        result5 = verify_claim_google_factcheck(full_statement)

        # Voting logic
        labels = ["FACT", "MYTH", "SCAM"]
        probs = [0, 0, 0]

        # NLI
        if result1 != "UNCERTAIN":
            probs[labels.index(result1)] += 1

        # # LoReN
        # if result2 != "UNKNOWN":
        #     probs[labels.index(result2)] += 1
        
        # ClaimBuster
        if result3 != "UNCERTAIN":
            probs[labels.index(result3)] += 1
        
        if result4 != "UNKNOWN":
            probs[labels.index(result4)] += 1
        
        if result5 != "UNKNOWN":
            probs[labels.index(result5)] += 1

        print(f"Results: {result1}, {result3}, {result4}, {result5}")
        final_verdict = labels[probs.index(max(probs))]
        return {"Success": final_verdict}
        
    except Exception as e:
        return {"Error": f"An error occurred: {str(e)}"}


# l = verify_claim("The earth is flat.")
# print(f"The claim 'The earth is flat.' is classified as: {l}")