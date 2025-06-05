

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

# Load pre-trained RoBERTa-large MNLI model
MODEL_NAME = "roberta-large-mnli"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# Custom labels mapped from Hugging Face's [entailment, neutral, contradiction]
LABELS = ["FACT", "MYTH", "SCAM"]


def predict_nli(claim: str, evidence: str):
    """
    Predict NLI relationship between a claim and evidence.
    Returns probabilities for [entailment, neutral, contradiction].
    """
    inputs = tokenizer.encode_plus(evidence, claim, return_tensors="pt", truncation=True)

    if inputs["input_ids"].shape[1] == tokenizer.model_max_length:
        print("[WARNING] Input text has been truncated.")

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = F.softmax(logits, dim=1)[0]
    return probs.tolist()


def avg_predict(claim: str, evidences: list[str]):
    """
    Averages NLI predictions over multiple evidence texts.
    Applies weighting to contradiction score (SCAM) for stronger impact.
    """
    scores = [0.0, 0.0, 0.0]  # [entailment, neutral, contradiction]

    print(f"\n[INFO] Evaluating claim: \"{claim}\"")

    for i, evidence in enumerate(evidences, start=1):
        evdc_scores = predict_nli(claim, evidence)
        print(f"\n[Evidence {i}]")
        print(f"Evidence: {evidence}")
        print(f"Scores: {evdc_scores}")
        scores = [s + e for s, e in zip(scores, evdc_scores)]

    # Normalize
    scores = [s / len(evidences) for s in scores]

    # Boost the 'contradiction' (SCAM) score
    scores[2] *= 2.5

    print(f"\n[INFO] Weighted average scores: {scores}")
    prediction = LABELS[scores.index(max(scores))]
    print(f"[RESULT] Final prediction: {prediction}")
    return prediction


def reformulate_claim(claim: str):
    """
    Reformulate ambiguous claims for better model understanding.
    Extendable with more mappings.
    """
    claim_mappings = {
        "The earth is flat.": "The earth is confirmed to be flat.",
        "The earth is not round.": "The earth is denied to be round.",
    }
    return claim_mappings.get(claim.strip(), claim.strip())


if __name__ == "__main__":
    # Example test
    claim = "Vaccines cause autism."
    evidences = [
        "Numerous scientific studies have found no link between vaccines and autism.",
        "Global health organizations state that vaccines are safe and effective.",
        "The incidence of autism has not increased in highly vaccinated populations."
    ]

    claim = reformulate_claim(claim)
    result = avg_predict(claim, evidences)
    print(f"\n[FINAL RESULT] The claim \"{claim}\" is classified as: {result}")
