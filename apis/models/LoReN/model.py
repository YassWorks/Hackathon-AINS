import spacy
from transformers import pipeline


nlp = spacy.load("en_core_web_sm")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def extract_phrases(claim):
    
    doc = nlp(claim)
    phrases = []
    for token in doc:
        if token.dep_ in ("nsubj", "ROOT", "dobj", "pobj"):
            subtree = " ".join([t.text for t in token.subtree])
            phrases.append(subtree)
    return list(set(phrases))


def classify_phrase(phrase):
    
    labels = ["FACT", "MYTH", "SCAM"]
    result = classifier(phrase, labels, hypothesis_template="This statement is a {}.")
    return result['labels'][0].upper()


def evaluate_claim(claim, sources: list[str]):
    
    full = claim + " Evidence: " + " ".join(sources)
    phrases = extract_phrases(full)
    # print(f"\nClaim: {claim}\nExtracted phrases: {phrases}")
    
    results = {}
    for phrase in phrases:
        classification = classify_phrase(phrase)
        results[phrase] = classification
    
    # FINAL VERDICT
    classifications = list(results.values())
    if "SCAM" in classifications:
        final_verdict = "SCAM"
    elif all(c == "FACT" for c in classifications):
        final_verdict = "FACT"
    else:
        final_verdict = "MYTH"
    
    return final_verdict


# if __name__ == "__main__":
    
#     final_verdict = evaluate_claim("The Eiffel Tower was built in 1889 in Paris")
#     print(f"\nFinal verdict: {final_verdict}")
#     print("Detailed results:")
    