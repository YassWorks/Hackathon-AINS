from transformers import pipeline


def classify_fake_news(text: str) -> str:

    try:
        classifier = pipeline("text-classification", 
                            model="winterForestStump/Roberta-fake-news-detector", 
                            tokenizer="winterForestStump/Roberta-fake-news-detector")
        
        result = classifier(text)
        
        if not result or not isinstance(result, list):
            return "SCAM"
        
        best_prediction = max(result, key=lambda x: x.get('score', 0))
        label = best_prediction.get('label', '').upper()
        confidence = best_prediction.get('score', 0.0)
        
        if label == 'FAKE' or label == 'LABEL_0':
            return "SCAM" if confidence > 0.8 else "MYTH"
        elif label == 'REAL' or label == 'LABEL_1':
            return "FACT"
        else:
            return "MYTH"
            
    except Exception:
        return "UNCERTAIN"