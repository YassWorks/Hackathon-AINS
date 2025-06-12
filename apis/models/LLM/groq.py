import os
from groq import Groq
from typing import List, Dict
import json
from dotenv import load_dotenv
import time
from threading import Lock
from collections import deque


load_dotenv(override=True)


# Rate limiter: max 50 requests per 60 seconds
_MAX_REQUESTS = 50
_WINDOW = 60  # seconds
_request_lock = Lock()
_request_timestamps = deque()


def classify_claim_with_groq(claim: str, apikey: str, sources: List[str] = None) -> Dict[str, any]:
    """
    Use Groq's Qwen3-32B model to verify claims with sophisticated reasoning.
    
    Args:
        claim (str): The claim to verify
        sources (List[str], optional): List of source texts for context
        
    Returns:
        Dict[str, any]: Classification result with reasoning
    """
    try:
        # Initialize Groq client
        client = Groq(api_key=apikey)
        
        # Prepare context from sources
        context = ""
        if sources and len(sources) > 0:
            context = "\n\nContext from reliable sources:\n"
            for i, source in enumerate(sources[:5], 1):  # Limit to top 5 sources
                if source and source.strip():
                    context += f"{i}. {source[:300]}...\n"
        
        # Create a comprehensive prompt for claim verification
        prompt = f"""You are an expert fact-checker with access to reliable information sources. Your task is to analyze the following claim and determine its veracity.

CLAIM TO VERIFY: "{claim}"
{context}

Please analyze this claim thoroughly and provide:

1. CLASSIFICATION: Choose ONE of the following:
   - FACT: The claim is factually accurate and supported by evidence
   - MYTH: The claim is false, misleading, or lacks sufficient evidence
   - SCAM: The claim appears to be deliberately deceptive or fraudulent

2. CONFIDENCE: Rate your confidence from 0.0 to 1.0

3. REASONING: Provide a clear explanation for your classification

4. KEY_EVIDENCE: List the most important evidence points

Respond in the following JSON format:
{{
    "classification": "FACT|MYTH|SCAM",
    "confidence": 0.0-1.0,
    "reasoning": "Your detailed reasoning here",
    "key_evidence": ["evidence point 1", "evidence point 2", ...],
    "sources_used": true/false
}}

Focus on accuracy, logical reasoning, and evidence-based conclusions."""

        # Enforce rate limit before calling Groq API
        with _request_lock:
            now = time.time()
            # remove timestamps outside the rolling window
            while _request_timestamps and _request_timestamps[0] <= now - _WINDOW:
                _request_timestamps.popleft()
            # if reached max requests, wait until oldest timestamp expires
            if len(_request_timestamps) >= _MAX_REQUESTS:
                sleep_time = _WINDOW - (now - _request_timestamps[0])
                time.sleep(sleep_time)
                now = time.time()
                while _request_timestamps and _request_timestamps[0] <= now - _WINDOW:
                    _request_timestamps.popleft()
            _request_timestamps.append(now)
        
        # Call Groq API with Qwen3-32B model
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",  
            messages=[
                {
                    "role": "system",
                    "content": "You are a highly accurate fact-checking AI that provides evidence-based analysis of claims. Always respond with valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent, factual responses
            max_tokens=1024,
            top_p=0.9
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Try to parse JSON response
        try:
            result = json.loads(response_text)
            
            # Validate required fields
            if "classification" not in result:
                result["classification"] = "UNCERTAIN"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "reasoning" not in result:
                result["reasoning"] = "Analysis completed"
                
            # Ensure classification is in expected format
            classification = result["classification"].upper()
            if classification not in ["FACT", "MYTH", "SCAM"]:
                classification = "UNCERTAIN"
            
            result["classification"] = classification
            result["model"] = "Groq Qwen2.5-32B"
            result["sources_analyzed"] = len(sources) if sources else 0
            
            return result
            
        except json.JSONDecodeError:
            # Fallback: try to extract classification from text
            response_upper = response_text.upper()
            if "FACT" in response_upper and "MYTH" not in response_upper:
                classification = "FACT"
            elif "SCAM" in response_upper:
                classification = "SCAM"
            elif "MYTH" in response_upper or "FALSE" in response_upper:
                classification = "MYTH"
            else:
                classification = "UNCERTAIN"
                
            return {
                "classification": classification,
                "confidence": 0.7,
                "reasoning": response_text,
                "key_evidence": [],
                "model": "Groq Qwen2.5-32B",
                "sources_analyzed": len(sources) if sources else 0,
                "raw_response": response_text
            }
            
    except Exception as e:
        print(f"Error in Groq classification: {str(e)}")
        return {
            "classification": "UNCERTAIN",
            "confidence": 0.0,
            "reasoning": f"Error occurred: {str(e)}",
            "key_evidence": [],
            "model": "Groq Qwen2.5-32B",
            "sources_analyzed": 0,
            "error": str(e)
        }


def groq_fact_check(claim: str, apikey: str, sources: List[str] = None) -> str:
    """
    Main fact-checking function compatible with the existing API structure.
    
    Args:
        claim (str): The claim to fact-check
        sources (List[str], optional): List of source texts for context
        
    Returns:
        str: "FACT", "MYTH", "SCAM", or "UNCERTAIN"
    """
    try:
        result = classify_claim_with_groq(claim, apikey, sources)
            
        return result.get("classification", "UNCERTAIN")
        
    except Exception as e:
        print(f"Error in Groq fact check: {str(e)}")
        return "UNCERTAIN"
    

def explain(claims: List[str], verdict: str, apikey: str, sources: List[str] = None):
    """
    Generate an explanation for the classification using Groq.
    
    Args:
        claim (str): The claim being explained
        verdict (str): The classification verdict ("FACT", "MYTH", "SCAM")
        sources (List[str], optional): List of source texts for context
        
    Returns:
        str: Explanation text
    """
    try:
        client = Groq(api_key=apikey)
        
        prompt = f"Explain why the following statement is a {verdict}. These are the arguments: {', '.join(claims)}. Sources: {', '.join(sources[:3])}. Provide a short detailed explanation under 100 words."

        # Enforce rate limit before calling Groq API
        with _request_lock:
            now = time.time()
            # remove timestamps outside the rolling window
            while _request_timestamps and _request_timestamps[0] <= now - _WINDOW:
                _request_timestamps.popleft()
            # if reached max requests, wait until oldest timestamp expires
            if len(_request_timestamps) >= _MAX_REQUESTS:
                sleep_time = _WINDOW - (now - _request_timestamps[0])
                time.sleep(sleep_time)
                now = time.time()
                while _request_timestamps and _request_timestamps[0] <= now - _WINDOW:
                    _request_timestamps.popleft()
            _request_timestamps.append(now)
        
        # Call Groq API with Qwen3-32B model
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
            {
                "role": "system",
                "content": "You are a highly accurate fact-checking AI that provides evidence-based analysis of claims. Always respond with valid JSON format."
            },
            {
                "role": "user",
                "content": prompt
            }
            ],
            temperature=0.1,
            max_tokens=512,
            top_p=0.9
        )
        
        response_text = completion.choices[0].message.content.strip()
        
        # Return the explanation text
        return response_text
                
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return "Error generating explanation"