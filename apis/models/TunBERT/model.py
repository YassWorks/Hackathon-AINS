import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import List, Dict, Tuple

# Load the TunBERT model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("not-lain/TunBERT")
model = AutoModelForSequenceClassification.from_pretrained("not-lain/TunBERT", trust_remote_code=True)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def preprocess_text(text: str) -> str:
    """
    Preprocess the input text for better model performance.
    """
    # Basic text cleaning
    text = text.strip()
    # Remove excessive whitespace
    text = ' '.join(text.split())
    return text

def classify_claim(claim: str) -> Dict[str, float]:
    """
    Classify a single claim using TunBERT.
    
    Args:
        claim (str): The claim to classify
        
    Returns:
        Dict[str, float]: Dictionary with classification scores
    """
    try:
        # Preprocess the claim
        processed_claim = preprocess_text(claim)
        
        # Tokenize the input
        inputs = tokenizer(
            processed_claim,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        )
        
        # Move inputs to device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Get predictions
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=-1)
          # Convert to numpy and get probabilities
        probs = probabilities.cpu().numpy()[0]
        
        # Map to class labels (assuming binary classification: 0=False, 1=True)
        # TunBERT typically does binary classification for factuality
        if len(probs) == 2:
            false_prob = float(probs[0])
            true_prob = float(probs[1])
            result = {
                "false_probability": false_prob,
                "true_probability": true_prob,
                "prediction": "TRUE" if true_prob > false_prob else "FALSE",
                "confidence": float(np.max(probs))
            }
        else:
            # Multi-class scenario
            max_prob_idx = int(np.argmax(probs))
            result = {
                "probabilities": probs.tolist(),
                "prediction": f"CLASS_{max_prob_idx}",
                "confidence": float(np.max(probs))
            }
        
        return result
        
    except Exception as e:
        print(f"Error in TunBERT classification: {str(e)}")
        return {
            "prediction": "UNCERTAIN",
            "confidence": 0.0,
            "error": str(e)
        }

def classify_with_context(claim: str, context_sources: List[str]) -> Dict[str, any]:
    """
    Classify a claim with additional context from sources.
    
    Args:
        claim (str): The claim to verify
        context_sources (List[str]): List of source texts to provide context
        
    Returns:
        Dict[str, any]: Classification result with context analysis
    """
    try:
        # First classify the claim alone
        claim_result = classify_claim(claim)
        
        # Analyze claim against each source
        source_results = []
        for i, source in enumerate(context_sources[:5]):  # Limit to top 5 sources
            if source and len(source.strip()) > 0:
                # Create a hypothesis-premise pair for entailment checking
                combined_text = f"Claim: {claim} Context: {source[:500]}"  # Limit source length
                source_result = classify_claim(combined_text)
                source_results.append({
                    "source_index": i,
                    "result": source_result,
                    "source_snippet": source[:200] + "..." if len(source) > 200 else source
                })
        
        # Aggregate results
        if source_results:
            # Calculate weighted average based on confidence
            total_weight = 0
            weighted_true_prob = 0
            
            for src_result in source_results:
                if "true_probability" in src_result["result"]:
                    confidence = src_result["result"]["confidence"]
                    true_prob = src_result["result"]["true_probability"]
                    weighted_true_prob += true_prob * confidence
                    total_weight += confidence
            
            if total_weight > 0:
                final_true_prob = weighted_true_prob / total_weight
                final_false_prob = 1 - final_true_prob
                
                return {
                    "prediction": "TRUE" if final_true_prob > 0.5 else "FALSE",
                    "confidence": abs(final_true_prob - 0.5) * 2,  # Normalize confidence
                    "true_probability": final_true_prob,
                    "false_probability": final_false_prob,
                    "claim_only_result": claim_result,
                    "source_analysis": source_results,
                    "sources_used": len(source_results)
                }
        
        # Fallback to claim-only result
        return {
            **claim_result,
            "claim_only_result": claim_result,
            "source_analysis": source_results,
            "sources_used": len(source_results)
        }
        
    except Exception as e:
        print(f"Error in TunBERT context classification: {str(e)}")
        return {
            "prediction": "UNCERTAIN",
            "confidence": 0.0,
            "error": str(e)
        }

def tunbert_fact_check(claim: str, sources: List[str] = None) -> str:
    """
    Main fact-checking function compatible with the existing API structure.
    
    Args:
        claim (str): The claim to fact-check
        sources (List[str], optional): List of source texts for context
        
    Returns:
        str: "FACT", "MYTH", or "UNCERTAIN"
    """
    try:
        if sources and len(sources) > 0:
            result = classify_with_context(claim, sources)
        else:
            result = classify_claim(claim)
        
        # Map TunBERT predictions to the expected labels
        if "error" in result:
            return "UNCERTAIN"
        
        prediction = result.get("prediction", "UNCERTAIN")
        confidence = result.get("confidence", 0.0)
        
        # Apply confidence threshold
        if confidence < 0.6:  # Low confidence threshold
            return "UNCERTAIN"
        
        # Map predictions to expected format
        if prediction == "TRUE":
            return "FACT"
        elif prediction == "FALSE":
            return "MYTH"
        else:
            return "UNCERTAIN"
            
    except Exception as e:
        print(f"Error in TunBERT fact check: {str(e)}")
        return "UNCERTAIN"

def get_detailed_analysis(claim: str, sources: List[str] = None) -> Dict[str, any]:
    """
    Get detailed analysis results from TunBERT for debugging/transparency.
    
    Args:
        claim (str): The claim to analyze
        sources (List[str], optional): List of source texts for context
        
    Returns:
        Dict[str, any]: Detailed analysis results
    """
    if sources and len(sources) > 0:
        return classify_with_context(claim, sources)
    else:
        return classify_claim(claim)