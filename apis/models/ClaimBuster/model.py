from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

model_name = "finetuneanon/claimbuster-lite"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

def predict_claimworthiness(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=1)[0]

    labels = ["Non-Checkworthy", "Checkworthy"]
    results = {label: prob.item() for label, prob in zip(labels, probs)}
    return results

if __name__ == "__main__":
    text = "The government will increase taxes next year."
    prediction = predict_claimworthiness(text)
    print(f"Input text: {text}")
    print(f"Prediction scores: {prediction}")
