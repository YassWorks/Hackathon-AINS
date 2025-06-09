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
def avg_predict(claim, evidences=[], threshold=0.5):
    
    if not evidences:
        return "NO_EVIDENCE"
    scores = torch.zeros(3)
    for evidence in evidences:
        probs = predict_nli(claim, evidence)
        scores += torch.tensor(probs)
    scores /= len(evidences)

    max_score, idx = torch.max(scores, dim=0)
    labels = ["FACT", "MYTH", "SCAM"]
    # if max_score < threshold:
    #     return "UNCERTAIN"
    return labels[idx.item()]


# if __name__ == "__main__":
    
#     claim = "Birds can fly."
#     evidences = [
#         "Most birds have wings and can fly.",
#         "Birds are known for their ability to fly.",
#         "The majority of birds are capable of flight, which is a key characteristic of the class Aves.",
#         "While many birds can fly, there are exceptions such as flightless birds like the kiwi and emu.",
#         "Birds are generally defined by their feathers and beaks, with flight being a common but not universal trait."
#     ]
    
#     result = avg_predict(claim, evidences)
#     print(f"The claim '{claim}' is classified as: {result}")