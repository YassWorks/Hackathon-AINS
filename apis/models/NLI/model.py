from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F


model_name = "ynie/roberta-large-snli_mnli_fever_anli_R1_R2_R3-nli"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)


# labels = ["entailment", "neutral", "contradiction"] in this order
def predict_nli(claim, evidence):
    
    inputs = tokenizer.encode_plus(evidence, claim, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=1)[0]
    return probs.tolist()


# classification based on given sources
def avg_predict(claim, evidences=[]):
    
    if not evidences:
        return "NO_EVIDENCE"
    scores = torch.zeros(3)
    for evidence in evidences:
        probs = predict_nli(claim, evidence)
        scores += torch.tensor(probs)
    scores /= len(evidences)

    max_score, idx = torch.max(scores, dim=0)
    labels = ["FACT", "MYTH", "SCAM"]
    
    return labels[idx.item()]