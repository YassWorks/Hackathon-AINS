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
from models.TunBERT.model import tunbert_fact_check, get_detailed_analysis
from models.LLM.groq import groq_fact_check, get_detailed_groq_analysis
from models.ClaimExtractor.model import extract_claims_from_text
from converters.converter import convert_to_text, is_supported_format
from translator.translate import translate_to_english
import threading
from dotenv import load_dotenv
from models.FakeNewsDetector.model import classify_fake_news
from models.Explainer.model import explain


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
            logger.info(f"[{request_id}] Using translated text as single claim after extraction failure")        # Step 4: Fact-checking each claim
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
            result1, result2, result3, result4, result5, result6 = None, None, None, None, None, None
            
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
                result6 = groq_fact_check(claim, sources)
                logger.info(f"[{request_id}] Groq result for claim {i+1}: {result6}")

            # Create and run threads for this claim
            logger.info(f"[{request_id}] Starting parallel execution of all models for claim {i+1}")
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
                thread.join()
            
            logger.info(f"[{request_id}] All models completed for claim {i+1}")

            # Voting logic for this claim with weighted votes
            labels = ["FACT", "MYTH", "SCAM"]
            probs = [0, 0, 0]

            # Count votes from each model
            model_results = {
                "NLI": result1,
                "ClaimBuster": result2,
                "SBERT": result3,
                "Google": result4,
                "TunBERT": result5,
                "Groq": result6
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

            logger.info(f"[{request_id}] Claim {i+1} vote counts: FACT={probs[0]}, MYTH={probs[1]}, SCAM={probs[2]}")
            print(f"Claim {i+1} Results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}, TunBERT={result5}, Groq={result6}")
            
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
        explanation_parts = [f"Overall verdict is {final_verdict}."]

        if claim_results:
            num_claims_analyzed = len(claim_results)
            explanation_parts.append(f"{num_claims_analyzed} claim(s) were analyzed.")

            # Add details from the first claim's analysis if available
            first_claim_analysis = claim_results[0]
            first_claim_verdict = first_claim_analysis.get("verdict")
            first_claim_confidence = first_claim_analysis.get("confidence", 0)
            explanation_parts.append(
            f"The primary claim was assessed as {first_claim_verdict} "
            f"with a confidence of {first_claim_confidence:.2f}."
            )

        if source_language != "en" and source_language != "auto":
            explanation_parts.append(f"Input was translated from {source_language}.")

        if files and len(files) > 0:
            explanation_parts.append(f"{len(files)} file(s) were processed.")

        # Summarize model contributions based on overall_votes
        contributing_models_summary = []
        for model_label, count in overall_votes.items():
            if count > 0:
                contributing_models_summary.append(f"{count} vote(s) for {model_label}")
        if contributing_models_summary:
            explanation_parts.append(f"Vote summary: {', '.join(contributing_models_summary)}.")
        else:
            explanation_parts.append("No definitive votes were cast by the models.")

        explanation = " ".join(explanation_parts)
        
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


@app.post("/classify-simple")
async def verify_claim_simple(
    prompt: str = Form(...),
    files: List[UploadFile] = File(None)
):
    """
    Legacy endpoint for backwards compatibility with the original simple classification.
    """
    try:
        full_statement = prompt  # Simple processing without full pipeline
        
        # Search for sources
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
            thread.join()

        # Voting logic
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
        "message": "ANTI-SCAM API with Comprehensive Fact-Checking Pipeline",
        "version": "2.0.0",
        "pipeline_features": [
            "Multi-format file processing (text, image, audio)",
            "Multi-language translation support",
            "Automatic claim extraction",
            "Ensemble fact-checking with 6 models",
            "Comprehensive analysis and confidence scoring"
        ],        "available_endpoints": [
            "/verify - Simplified fact-checking endpoint (recommended)",
            "/classify - Complete fact-checking pipeline with file upload and translation",
            "/classify-simple - Legacy simple classification endpoint", 
            "/tunbert-analyze - Detailed TunBERT analysis",
            "/groq-analyze - Detailed Groq Qwen3-32B analysis",
            "/models/status - Check model availability",
            "/docs - API documentation"
        ],
        "supported_languages": ["auto", "en", "fr", "ar", "tunisian_ar", "transliterated_ar"],
        "supported_file_formats": {
            "text": [".txt", ".md", ".rtf", ".csv", ".json", ".xml", ".html"],
            "image": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"],
            "audio": [".wav", ".flac", ".aiff", ".aifc"]
        },
        "models": ["NLI", "ClaimBuster", "SBERT", "Google Fact Check", "TunBERT", "Groq Qwen2.5-32B"]
    }


@app.post("/verify")
async def verify_single(
    prompt: str = Form(...),
    files: List[UploadFile] = File(None),
    source_language: str = Form("auto")
):
    """
    Single endpoint for fact verification that returns a simplified response.
    Returns: {"Success": {"Verdict": verdict, "Explanation": explanation}}
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] Starting /verify request")
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
            return {"Success": {"Verdict": "UNCERTAIN", "Explanation": "No valid text could be extracted from the provided input"}}
        
        # Step 2: Translation to English
        logger.info(f"[{request_id}] STEP 2: Starting translation")
        translated_text = combined_text
        if source_language != "en" and source_language != "auto":
            logger.info(f"[{request_id}] Translating from {source_language} to English")
            try:
                translated_text = await translate_to_english(combined_text, source_language)
                if translated_text.startswith("Error"):
                    logger.warning(f"[{request_id}] Translation failed: {translated_text}")
                    translated_text = combined_text
                    logger.info(f"[{request_id}] Using original text after translation failure")
                else:
                    logger.info(f"[{request_id}] Translation successful. Translated text length: {len(translated_text)} characters")
                    logger.debug(f"[{request_id}] Translated text preview: '{translated_text[:200]}{'...' if len(translated_text) > 200 else ''}'")
            except Exception as e:
                logger.error(f"[{request_id}] Translation error: {str(e)}")
                translated_text = combined_text
                logger.info(f"[{request_id}] Using original text after translation exception")
        else:
            logger.info(f"[{request_id}] No translation needed (language: {source_language})")
        
        # Step 3: Claim Extraction
        logger.info(f"[{request_id}] STEP 3: Starting claim extraction")
        try:
            extracted_claims = extract_claims_from_text(translated_text)
            logger.info(f"[{request_id}] Extracted {len(extracted_claims) if extracted_claims else 0} claims")
            
            if not extracted_claims or len(extracted_claims) == 0:
                extracted_claims = [translated_text]
                logger.info(f"[{request_id}] No claims extracted, using full translated text as single claim")
            else:
                for i, claim in enumerate(extracted_claims):
                    logger.debug(f"[{request_id}] Claim {i+1}: '{claim[:100]}{'...' if len(claim) > 100 else ''}'")
            
            claims_to_process = extracted_claims[:3]  # Limit to top 3 claims
            logger.info(f"[{request_id}] Processing top {len(claims_to_process)} claims")
            
        except Exception as e:
            logger.error(f"[{request_id}] Claim extraction error: {str(e)}")
            claims_to_process = [translated_text]
            logger.info(f"[{request_id}] Using translated text as single claim after extraction failure")        # Step 4: Fact-checking - use the primary claim for analysis
        logger.info(f"[{request_id}] STEP 4: Starting fact-checking")
        primary_claim = claims_to_process[0]
        logger.info(f"[{request_id}] Primary claim: '{primary_claim[:100]}{'...' if len(primary_claim) > 100 else ''}'")
        
        logger.info(f"[{request_id}] Searching for sources")
        sources = search_topic(primary_claim, num_paragraphs=20)
        logger.info(f"[{request_id}] Found {len(sources)} sources")
        
        # Use original combined text for TunBERT (before translation)
        original_claim_for_tunbert = combined_text
        logger.info(f"[{request_id}] TunBERT will use original text (length: {len(original_claim_for_tunbert)} chars)")
        
        # Get predictions from different models
        result1, result2, result3, result4, result5, result6 = None, None, None, None, None, None

        def run_avg_predict():
            nonlocal result1
            logger.info(f"[{request_id}] Running NLI model")
            result1 = avg_predict(primary_claim, sources)
            logger.info(f"[{request_id}] NLI result: {result1}")

        def run_verify_claim_claimbuster():
            nonlocal result2
            logger.info(f"[{request_id}] Running ClaimBuster model")
            result2 = verify_claim_claimbuster(primary_claim, CLAIM_BUSTER_API_KEY)
            logger.info(f"[{request_id}] ClaimBuster result: {result2}")

        def run_sbert_predict():
            nonlocal result3
            logger.info(f"[{request_id}] Running SBERT model")
            result3 = sbert_predict(primary_claim, sources)
            logger.info(f"[{request_id}] SBERT result: {result3}")

        def run_verify_claim_google_factcheck():
            nonlocal result4
            logger.info(f"[{request_id}] Running Google FactCheck model")
            result4 = verify_claim_google_factcheck(primary_claim, GOOGLE_API_KEY)
            logger.info(f"[{request_id}] Google FactCheck result: {result4}")

        def run_tunbert_predict():
            nonlocal result5
            logger.info(f"[{request_id}] Running TunBERT model (using original text)")
            # TunBERT gets the original text before translation
            result5 = tunbert_fact_check(original_claim_for_tunbert, sources)
            logger.info(f"[{request_id}] TunBERT result: {result5}")

        def run_groq_predict():
            nonlocal result6
            logger.info(f"[{request_id}] Running Groq model")
            result6 = groq_fact_check(primary_claim, sources)
            logger.info(f"[{request_id}] Groq result: {result6}")

        # Create and run threads
        logger.info(f"[{request_id}] Starting parallel execution of all models")
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
            thread.join()
        
        logger.info(f"[{request_id}] All models completed")

        # Voting logic with weighted votes
        logger.info(f"[{request_id}] STEP 5: Starting voting")
        labels = ["FACT", "MYTH", "SCAM"]
        votes = {"FACT": 0, "MYTH": 0, "SCAM": 0}
        model_results = [result1, result2, result3, result4, result5, result6]
        model_names = ["NLI", "ClaimBuster", "SBERT", "Google", "TunBERT", "Groq"]
        
        logger.info(f"[{request_id}] Model results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}, TunBERT={result5}, Groq={result6}")
        
        # Count votes from each model with weights
        confident_predictions = []
        for i, result in enumerate(model_results):
            if result and result not in ["UNCERTAIN", "UNKNOWN"]:
                # Groq gets 3x voting power, others get 1x
                weight = 3 if model_names[i] == "Groq" else 1
                votes[result] += weight
                confident_predictions.append(f"{model_names[i]}: {result}")
                logger.debug(f"[{request_id}] {model_names[i]} voted {result} (weight: {weight})")

        logger.info(f"[{request_id}] Vote counts: FACT={votes['FACT']}, MYTH={votes['MYTH']}, SCAM={votes['SCAM']}")
        print(f"Results: NLI={result1}, ClaimBuster={result2}, SBERT={result3}, Google={result4}, TunBERT={result5}, Groq={result6}")
        
        # Determine final verdict
        logger.info(f"[{request_id}] STEP 6: Determining final verdict")
        if sum(votes.values()) == 0:
            final_verdict = "UNCERTAIN"
            explanation = "No models provided confident predictions for this claim."
            logger.info(f"[{request_id}] Final verdict: UNCERTAIN (no confident predictions)")
        else:
            final_verdict = max(votes, key=votes.get)
            
            # Generate explanation
            total_votes = sum(votes.values())
            winning_votes = votes[final_verdict]
            confidence_pct = int((winning_votes / total_votes) * 100) if total_votes > 0 else 0
            
            explanation = f"Classified as {final_verdict} with {confidence_pct}% confidence ({winning_votes}/{total_votes} weighted votes). "
            
            if len(claims_to_process) > 1:
                explanation += f"Analysis based on {len(claims_to_process)} extracted claims. "
            
            if source_language != "en" and source_language != "auto":
                explanation += f"Text was translated from {source_language} to English. "
            
            if files and len(files) > 0:
                explanation += f"Content extracted from {len(files)} uploaded file(s). "
            
            if confident_predictions:
                explanation += f"Contributing models: {', '.join(confident_predictions[:3])}."
            
            logger.info(f"[{request_id}] Final verdict: {final_verdict} ({confidence_pct}% confidence)")
        
        logger.info(f"[{request_id}] Request completed successfully")
        logger.info(f"[{request_id}] Response: Verdict={final_verdict}, Explanation='{explanation[:100]}{'...' if len(explanation) > 100 else ''}'")
        
        return {
            "Success": {
                "Verdict": final_verdict,
                "Explanation": explanation.strip()
            }
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] ERROR: {str(e)}", exc_info=True)
        return {
            "Success": {
                "Verdict": "UNCERTAIN", 
                "Explanation": f"An error occurred during analysis: {str(e)}"
            }
        }