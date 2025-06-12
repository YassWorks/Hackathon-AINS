from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import tempfile
import asyncio
import logging
from datetime import datetime
from models.NLI.model import avg_predict
from web_searcher.app import search_topic
from models.ClaimBuster.model import verify_claim_claimbuster
from models.SBERT.model import sbert_predict
from models.Google.model import verify_claim_google_factcheck
from models.TunBERT.model import tunbert_fact_check
from models.LLM.groq import groq_fact_check, explain
from models.ClaimExtractor.model import extract_claims_from_text
from converters.converter import convert_to_text, is_supported_format
from translator.translate import translate_to_english
import threading
from dotenv import load_dotenv
from models.FakeNewsDetector.model import classify_fake_news


load_dotenv()


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("AINS_API")


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
    files: List[UploadFile] = File(None),
    source_language: str = Form("auto")  # auto, en, fr, ar, tunisian_ar, transliterated_ar
):
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Starting classification request")
    logger.info(f"[{request_id}] Input prompt: '{prompt[:100]}{'...' if len(prompt) > 100 else ''}'")
    logger.info(f"[{request_id}] Source language: {source_language}")
    logger.info(f"[{request_id}] Number of files: {len(files) if files else 0}")
    
    try:
        # Step 1: Data Extraction
        logger.info(f"[{request_id}] STEP 1: Starting data extraction")
        extracted_texts = []
        
        # Add the user prompt as base text
        if prompt and prompt.strip():
            extracted_texts.append(prompt.strip())
            logger.info(f"[{request_id}] Added user prompt to extracted texts")
        
        # Extract text from uploaded files
        if files:
            logger.info(f"[{request_id}] Processing {len(files)} uploaded files")
            for i, file in enumerate(files):
                if file.filename and file.size > 0:
                    logger.info(f"[{request_id}] Processing file {i+1}: {file.filename} ({file.size} bytes)")
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as temp_file:
                            content = await file.read()
                            temp_file.write(content)
                            temp_file_path = temp_file.name
                        
                        # Check if file format is supported
                        if is_supported_format(temp_file_path):
                            logger.info(f"[{request_id}] File format supported, extracting text...")
                            extracted_text = convert_to_text(temp_file_path)
                            if extracted_text and not extracted_text.startswith("[ERROR]"):
                                extracted_texts.append(extracted_text)
                                logger.info(f"[{request_id}] Successfully extracted {len(extracted_text)} characters from {file.filename}")
                            else:
                                logger.warning(f"[{request_id}] Failed to extract text from {file.filename}: {extracted_text}")
                        else:
                            logger.warning(f"[{request_id}] Unsupported file format: {file.filename}")
                        
                        # Clean up temporary file
                        os.unlink(temp_file_path)
                        
                    except Exception as e:
                        logger.error(f"[{request_id}] Error processing file {file.filename}: {str(e)}")
                        continue
        
        # Combine all extracted texts
        combined_text = " ".join(extracted_texts)
        logger.info(f"[{request_id}] Combined text length: {len(combined_text)} characters")
        logger.debug(f"[{request_id}] Combined text preview: '{combined_text[:200]}{'...' if len(combined_text) > 200 else ''}'")
        
        if not combined_text.strip():
            logger.warning(f"[{request_id}] No valid text could be extracted")
            return {"Error": "No valid text could be extracted from the provided input"}
        
        # Step 2: Translation to English
        logger.info(f"[{request_id}] STEP 2: Starting translation")
        translated_text = combined_text
        if source_language != "en" and source_language != "auto":
            logger.info(f"[{request_id}] Translating from {source_language} to English")
            try:
                translated_text = await translate_to_english(combined_text, source_language)
                if translated_text.startswith("Error"):
                    logger.warning(f"[{request_id}] Translation failed: {translated_text}")
                    # If translation fails, proceed with original text
                    translated_text = combined_text
                    logger.info(f"[{request_id}] Using original text after translation failure")
                else:
                    logger.info(f"[{request_id}] Translation successful. Translated text length: {len(translated_text)} characters")
                    logger.debug(f"[{request_id}] Translated text preview: '{translated_text[:200]}{'...' if len(translated_text) > 200 else ''}'")
            except Exception as e:
                logger.error(f"[{request_id}] Translation error: {str(e)}")
                # Proceed with original text if translation fails
                translated_text = combined_text
                logger.info(f"[{request_id}] Using original text after translation exception")
        else:
            logger.info(f"[{request_id}] No translation needed (language: {source_language})")
        
        # Step 3: Claim Extraction
        logger.info(f"[{request_id}] STEP 3: Starting claim extraction")
        try:
            extracted_claims = extract_claims_from_text(translated_text)
            logger.info(f"[{request_id}] Extracted {len(extracted_claims) if extracted_claims else 0} claims")
            
            # If no claims extracted or extraction failed, use the translated text as the claim
            if not extracted_claims or len(extracted_claims) == 0:
                extracted_claims = [translated_text]
                logger.info(f"[{request_id}] No claims extracted, using full translated text as single claim")
            else:
                for i, claim in enumerate(extracted_claims):
                    logger.debug(f"[{request_id}] Claim {i+1}: '{claim[:100]}{'...' if len(claim) > 100 else ''}'")
            
            # Limit to top 3 claims for processing efficiency
            claims_to_process = extracted_claims[:3]
            logger.info(f"[{request_id}] Processing top {len(claims_to_process)} claims")
            
        except Exception as e:
            logger.error(f"[{request_id}] Claim extraction error: {str(e)}")
            # Fallback to using the translated text as a single claim
            claims_to_process = [translated_text]
            logger.info(f"[{request_id}] Using translated text as single claim after extraction failure")      
            
        # Step 4: Fact-checking each claim
        logger.info(f"[{request_id}] STEP 4: Starting fact-checking for {len(claims_to_process)} claims")
        claim_results = []
        overall_votes = {"FACT": 0, "MYTH": 0, "SCAM": 0}
        
        for i, claim in enumerate(claims_to_process):
            logger.info(f"[{request_id}] Processing claim {i+1}/{len(claims_to_process)}")
            logger.debug(f"[{request_id}] Claim {i+1} text: '{claim[:100]}{'...' if len(claim) > 100 else ''}'")
            
            # Search for sources for this specific claim
            logger.info(f"[{request_id}] Searching for sources for claim {i+1}")
            sources = search_topic(claim, num_paragraphs=20)
            logger.info(f"[{request_id}] Found {len(sources)} sources for claim {i+1}")
            
            # Get predictions from different models for this claim
            result1, result2, result3, result4, result5, result6, result7 = None, None, None, None, None, None, None
            
            # Use original combined text for TunBERT (before translation)
            original_claim_for_tunbert = extracted_texts[i] if i < len(extracted_texts) else combined_text
            logger.info(f"[{request_id}] TunBERT will use original text (length: {len(original_claim_for_tunbert)} chars)")

            def run_avg_predict():
                nonlocal result1
                logger.info(f"[{request_id}] Running NLI model for claim {i+1}")
                result1 = avg_predict(claim, sources)
                logger.info(f"[{request_id}] NLI result for claim {i+1}: {result1}")

            def run_verify_claim_claimbuster():
                nonlocal result2
                logger.info(f"[{request_id}] Running ClaimBuster model for claim {i+1}")
                result2 = verify_claim_claimbuster(claim, CLAIM_BUSTER_API_KEY)
                logger.info(f"[{request_id}] ClaimBuster result for claim {i+1}: {result2}")

            def run_sbert_predict():
                nonlocal result3
                logger.info(f"[{request_id}] Running SBERT model for claim {i+1}")
                result3 = sbert_predict(claim, sources)
                logger.info(f"[{request_id}] SBERT result for claim {i+1}: {result3}")

            def run_verify_claim_google_factcheck():
                nonlocal result4
                logger.info(f"[{request_id}] Running Google FactCheck model for claim {i+1}")
                result4 = verify_claim_google_factcheck(claim, GOOGLE_API_KEY)
                logger.info(f"[{request_id}] Google FactCheck result for claim {i+1}: {result4}")

            def run_tunbert_predict():
                nonlocal result5
                logger.info(f"[{request_id}] Running TunBERT model for claim {i+1} (using original text)")
                # TunBERT gets the original text before translation
                result5 = tunbert_fact_check(original_claim_for_tunbert, sources)
                logger.info(f"[{request_id}] TunBERT result for claim {i+1}: {result5}")

            def run_groq_predict():
                nonlocal result6
                logger.info(f"[{request_id}] Running Groq model for claim {i+1}")
                result6 = groq_fact_check(claim, GROQ_API_KEY, sources)
                logger.info(f"[{request_id}] Groq result for claim {i+1}: {result6}")

            def run_fake_news_classify():
                nonlocal result7
                logger.info(f"[{request_id}] Running FakeNewsDetector model for claim {i+1}")
                result7 = classify_fake_news(claim)
                logger.info(f"[{request_id}] FakeNewsDetector result for claim {i+1}: {result7}")

            # Create and run threads for this claim
            logger.info(f"[{request_id}] Starting parallel execution of all models for claim {i+1}")
            threads = [
                threading.Thread(target=run_avg_predict),
                threading.Thread(target=run_verify_claim_claimbuster),
                threading.Thread(target=run_sbert_predict),
                threading.Thread(target=run_verify_claim_google_factcheck),
                threading.Thread(target=run_tunbert_predict),
                threading.Thread(target=run_groq_predict),
                threading.Thread(target=run_fake_news_classify),
            ]

            # Start threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            logger.info(f"[{request_id}] All models completed for claim {i+1}")

            # Voting logic for this claim with weighted votes
            labels = ["FACT", "MYTH", "SCAM"]
            probs = [0, 0, 0]            # Count votes from each model
            model_results = {
                "NLI": result1,
                "ClaimBuster": result2,
                "SBERT": result3,
                "Google": result4,
                "TunBERT": result5,
                "Groq": result6,
                "FakeNewsDetector": result7
            }

            logger.info(f"[{request_id}] Voting for claim {i+1} - Model results: {model_results}")

            # NLI (weight: 1)
            if result1 and result1 != "UNCERTAIN":
                probs[labels.index(result1)] += 1
                logger.debug(f"[{request_id}] NLI voted {result1} (weight: 1)")
            
            # ClaimBuster (weight: 1)
            if result2 and result2 != "UNCERTAIN":
                probs[labels.index(result2)] += 1
                logger.debug(f"[{request_id}] ClaimBuster voted {result2} (weight: 1)")
            
            # SBERT (weight: 1)
            if result3 and result3 != "UNKNOWN":
                probs[labels.index(result3)] += 1
                logger.debug(f"[{request_id}] SBERT voted {result3} (weight: 1)")
            
            # Google Fact Check (weight: 1)
            if result4 and result4 != "UNKNOWN":
                probs[labels.index(result4)] += 1
                logger.debug(f"[{request_id}] Google voted {result4} (weight: 1)")
            
            # TunBERT (weight: 1)
            if result5 and result5 != "UNCERTAIN":
                probs[labels.index(result5)] += 1
                logger.debug(f"[{request_id}] TunBERT voted {result5} (weight: 1)")
              # Groq Qwen3-32B (weight: 3 - highest voting power)
            if result6 and result6 != "UNCERTAIN":
                probs[labels.index(result6)] += 3
                logger.debug(f"[{request_id}] Groq voted {result6} (weight: 3)")

            # FakeNewsDetector (weight: 1)
            if result7 and result7 != "UNCERTAIN":
                probs[labels.index(result7)] += 1
                logger.debug(f"[{request_id}] FakeNewsDetector voted {result7} (weight: 1)")

            logger.info(f"[{request_id}] Claim {i+1} vote counts: FACT={probs[0]}, MYTH={probs[1]}, SCAM={probs[2]}")
            print(f"Claim {i+1} Results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}, TunBERT={result5}, Groq={result6}, FakeNewsDetector={result7}")
            
            # Handle case where no model gives a confident prediction for this claim
            if max(probs) == 0:
                claim_verdict = "UNCERTAIN"
                logger.info(f"[{request_id}] Claim {i+1} verdict: UNCERTAIN (no confident predictions)")
            else:
                claim_verdict = labels[probs.index(max(probs))]
                logger.info(f"[{request_id}] Claim {i+1} verdict: {claim_verdict} (winning votes: {max(probs)})")
            
            # Add to overall votes (excluding UNCERTAIN)
            if claim_verdict != "UNCERTAIN":
                overall_votes[claim_verdict] += 1
                logger.debug(f"[{request_id}] Added {claim_verdict} to overall votes")
            
            # Store result for this claim
            claim_results.append({
                "claim": claim,
                "verdict": claim_verdict,
                "model_results": model_results,
                "vote_counts": dict(zip(labels, probs)),
                "confidence": max(probs) / sum(probs) if sum(probs) > 0 else 0
            })
        
        # Step 5: Determine overall verdict
        logger.info(f"[{request_id}] STEP 5: Determining overall verdict")
        logger.info(f"[{request_id}] Overall vote summary: {overall_votes}")
        
        if sum(overall_votes.values()) == 0:
            final_verdict = "UNCERTAIN"
            logger.info(f"[{request_id}] Final verdict: UNCERTAIN (no claims had confident predictions)")
        else:
            final_verdict = max(overall_votes, key=overall_votes.get)
            logger.info(f"[{request_id}] Final verdict: {final_verdict} (winning category: {overall_votes[final_verdict]} votes)")
        
        # Step 6: Prepare comprehensive response
        logger.info(f"[{request_id}] STEP 6: Preparing response")

        explanation = explain(claims_to_process, final_verdict, GROQ_API_KEY, sources)
        
        logger.info(f"[{request_id}] Request completed successfully")
        logger.info(f"[{request_id}] Final response: Verdict={final_verdict}, Explanation='{explanation[:100]}{'...' if len(explanation) > 100 else ''}'")

        return {
            "Success": {
            "Verdict": final_verdict,
            "Explanation": explanation
            }
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] ERROR: {str(e)}", exc_info=True)
        return {"Error": f"An error occurred: {str(e)}"}