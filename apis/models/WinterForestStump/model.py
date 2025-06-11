from transformers import pipeline
import time
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WinterForestFakeNewsDetector:
    def __init__(self, hf_token: Optional[str] = None):
        
        self.model_name = "winterForestStump/Roberta-fake-news-detector"
        
        # Load the model locally
        logger.info(f"Loading model {self.model_name} locally...")
        try:
            self.classifier = pipeline("text-classification", 
                                     model=self.model_name, 
                                     tokenizer=self.model_name)
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect_fake_news(self, text: str, max_retries: int = 3) -> Dict:
        try:
            # Use the local model
            result = self.classifier(text)
            return self._parse_result(result, text)
            
        except Exception as e:
            logger.error(f"Model inference failed: {e}")
            return self._error_result(str(e), text)
    
    def _parse_result(self, api_result: List[Dict], original_text: str) -> Dict:
        try:
            if not api_result or not isinstance(api_result, list):
                return self._error_result("Invalid API response format", original_text)
            
            # Find the highest confidence prediction
            best_prediction = max(api_result, key=lambda x: x.get('score', 0))
            
            label = best_prediction.get('label', '').upper()
            confidence = best_prediction.get('score', 0.0)
            
            # Map model labels to our classification system
            # Based on the model documentation: FAKE = fake news, REAL = real news
            if label == 'FAKE':
                classification = "myth"  # Fake news = myth in our system
                is_fake = True
            elif label == 'REAL':
                classification = "real"
                is_fake = False
            else:
                # Check if it's using LABEL_0/LABEL_1 format
                if label == 'LABEL_0':
                    # According to model page: 0 = Fake news
                    classification = "myth"
                    is_fake = True
                elif label == 'LABEL_1':
                    # According to model page: 1 = Real news
                    classification = "real"
                    is_fake = False
                else:
                    # Fallback - assume real if uncertain
                    classification = "real"
                    is_fake = False
                    confidence = 0.5
                    logger.warning(f"Unknown label format: {label}")
            
            # Generate reasoning
            confidence_desc = "high" if confidence > 0.8 else "moderate" if confidence > 0.6 else "low"
            reasoning = f"Model classified as {label} with {confidence_desc} confidence ({confidence:.2f})"
            
            if is_fake:
                reasoning += " - Content appears to contain misinformation or be fake news"
            else:
                reasoning += " - Content appears to be legitimate news"
            
            return {
                "classification": classification,
                "confidence": confidence,
                "reasoning": reasoning,
                "is_fake_news": is_fake,
                "model_label": label,
                "model_name": "winterForestStump/Roberta-fake-news-detector",
                "all_predictions": api_result,
                "text_preview": original_text[:100] + "..." if len(original_text) > 100 else original_text,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error parsing result: {e}")
            return self._error_result(f"Parsing error: {str(e)}", original_text)
    
    def _error_result(self, error_msg: str, original_text: str) -> Dict:
        """Generate error result"""
        return {
            "classification": "error",  # Changed from "real" to "error"
            "confidence": 0.0,
            "reasoning": f"Error during analysis: {error_msg}",
            "is_fake_news": False,
            "model_label": "ERROR",
            "model_name": "winterForestStump/Roberta-fake-news-detector",
            "error": error_msg,
            "text_preview": original_text[:100] + "..." if len(original_text) > 100 else original_text,
            "timestamp": time.time()
        }
    
    def batch_detect(self, texts: List[str], delay: float = 1.0) -> List[Dict]:
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}")
            
            result = self.detect_fake_news(text)
            results.append(result)
            
            # Rate limiting
            if i < len(texts) - 1:  # Don't sleep after last request
                time.sleep(delay)
        
        return results
    
    def get_summary_stats(self, results: List[Dict]) -> Dict:
        if not results:
            return {"error": "No results to analyze"}
        
        total = len(results)
        fake_count = sum(1 for r in results if r.get("is_fake_news", False))
        real_count = sum(1 for r in results if not r.get("is_fake_news", False) and r.get("classification") != "error")
        error_count = sum(1 for r in results if r.get("classification") == "error")
        
        avg_confidence = sum(r.get("confidence", 0) for r in results if r.get("classification") != "error")
        non_error_count = total - error_count
        if non_error_count > 0:
            avg_confidence = avg_confidence / non_error_count
        else:
            avg_confidence = 0
        
        return {
            "total_analyzed": total,
            "fake_news_count": fake_count,
            "real_news_count": real_count,
            "error_count": error_count,
            "fake_percentage": (fake_count / total) * 100 if total > 0 else 0,
            "real_percentage": (real_count / total) * 100 if total > 0 else 0,
            "error_percentage": (error_count / total) * 100 if total > 0 else 0,
            "average_confidence": avg_confidence
        }

# Alternative models to try if the main one doesn't work
ALTERNATIVE_MODELS = [
    "hamzab/roberta-fake-news-classification",
    "jy46604790/Fake-News-Bert-Detect", 
    "vikram71198/distilroberta-base-finetuned-fake-news-detection"
]

def try_alternative_model(model_name: str, hf_token: str = None):
    class AlternativeDetector(WinterForestFakeNewsDetector):
        def __init__(self, model_name: str, hf_token: Optional[str] = None):
            self.model_name = model_name
            self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
            self.headers = {"Content-Type": "application/json"}
            
            if hf_token:
                self.headers["Authorization"] = f"Bearer {hf_token}"
    
    return AlternativeDetector(model_name, hf_token)

# Convenience functions
def is_fake_news(text: str, hf_token: str = None) -> bool:
    detector = WinterForestFakeNewsDetector(hf_token)
    result = detector.detect_fake_news(text)
    return result.get("is_fake_news", False)

def analyze_news_text(text: str, hf_token: str = None) -> Dict:
    detector = WinterForestFakeNewsDetector(hf_token)
    return detector.detect_fake_news(text)

# Example usage and testing
def main():
    """Example usage of the WinterForest fake news detector"""
    
    print("Testing model availability...")
    
    # Initialize detector (add your HF token for better rate limits)
    # Add your token here: WinterForestFakeNewsDetector("your_hf_token_here")
    detector = WinterForestFakeNewsDetector("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")
    
    # Test cases
    test_texts = [
        # Likely fake news
        "BREAKING: Scientists discover that drinking bleach cures all diseases! Big Pharma doesn't want you to know this secret!",
        
        # Likely real news
        "The Federal Reserve announced a 0.25% interest rate increase following their monthly meeting to address inflation concerns.",
        
        # Test with shorter text
        "COVID vaccines are safe and effective according to health authorities."
    ]
    
    print("=" * 60)
    print("WinterForest Fake News Detection Results")
    print("=" * 60)
    
    # Test with one example first
    print(f"\n--- Test Case 1 ---")
    text = test_texts[0]
    print(f"Text: {text}")
    print("-" * 40)
    
    result = detector.detect_fake_news(text)
    
    print(f"Classification: {result['classification'].upper()}")
    print(f"Is Fake News: {result['is_fake_news']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Model Label: {result['model_label']}")
    print(f"Reasoning: {result['reasoning']}")
    
    if 'error' in result:
        print(f"⚠️  Error: {result['error']}")
        print("\nTrying alternative models...")
        
        # Try alternative models
        for alt_model in ALTERNATIVE_MODELS:
            print(f"\nTrying: {alt_model}")
            try:
                alt_detector = try_alternative_model(alt_model)
                alt_result = alt_detector.detect_fake_news(text)
                if alt_result.get('classification') != 'error':
                    print(f"✅ Success with {alt_model}!")
                    print(f"Classification: {alt_result['classification']}")
                    print(f"Confidence: {alt_result['confidence']:.2f}")
                    break
                else:
                    print(f"❌ {alt_model} also failed: {alt_result.get('error', 'Unknown error')}")
            except Exception as e:
                print(f"❌ {alt_model} failed: {str(e)}")

if __name__ == "__main__":
    main()