from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# model (local)
model_name = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# labels = ["entailment", "neutral", "contradiction"] in this order
def predict_nli(claim, evidence):
    
    inputs = tokenizer.encode_plus(evidence, claim, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=1)[0]
    return probs.tolist()

# classification based on given sources
def avg_predict(claim, evidences=[]) -> str:
    
    scores = [0, 0, 0]
    for evidence in evidences:
        evdc_scores = predict_nli(claim, evidence)
        scores[evdc_scores.index(max(evdc_scores))] += 1
    
    m = max(scores)
    labels = ["FACT", "MYTH", "SCAM"]
    return labels[scores.index(m)]

if __name__ == "__main__":
    claim = "The earth is flat."
    evidences = [
        "Scientific studies show that the earth is round.",
        "Photos from space clearly depict a spherical earth.",
        "The curvature of the earth is visible from high altitudes."
    ]
    
    result = avg_predict(claim, evidences)
    print(f"The claim '{claim}' is classified as: {result}")