from sentence_transformers import SentenceTransformer, util
import torch

# Load SBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and lightweight, good performance
model.eval()


# Pre-processing function
def preprocess_text(text: str) -> str:
    """
    Pre-process input text by cleaning, lowercasing, and normalizing.
    """
    if not text:
        return ""
    return text.strip().lower()


def sbert_similarity_score(claim: str, evidence: str) -> float:
    """
    Compute the cosine similarity between the SBERT embeddings of the claim and the evidence.
    Returns a score between 0 and 1.
    """
    claim, evidence = preprocess_text(claim), preprocess_text(evidence)

    with torch.no_grad():
        embeddings = model.encode([claim, evidence], convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
        return similarity


def sbert_predict(claim: str, evidences: list[str]) -> str:
    """
    Take a claim and list of evidences. Compute average SBERT similarity score.
    Return prediction label: "SCAM" or "GENUINE" based on a threshold.
    """
    if not evidences:
        return "UNKNOWN"

    # Preprocess claims and evidences
    evidences = [preprocess_text(ev) for ev in evidences]
    claim = preprocess_text(claim)

    # Compute similarity scores
    scores = [sbert_similarity_score(claim, ev) for ev in evidences]

    # Option 1: Average score
    avg_score = sum(scores) / len(scores)

    print("\n[SBERT MODEL] Similarity scores:", scores)
    print("[SBERT MODEL] Average similarity:", avg_score)

    # Adjust threshold heuristically based on domain knowledge
    if avg_score > 0.7:
        classification = "FACT"
    elif 0.4 <= avg_score <= 0.7:
        classification = "MYTH"
    else:
        classification = "SCAM"

    return classification



# Example usage
'''
if __name__ == "__main__":
    claim = "The Earth is flat."
    evidences = [
        "The Earth is round based on scientific evidence.",
        "Satellite images confirm the Earth is spherical.",
        "The curvature of the Earth is observable from a plane."
    ]

    prediction = sbert_predict(claim, evidences)
    print(f"The claim '{claim}' is classified as: {prediction}")
'''
