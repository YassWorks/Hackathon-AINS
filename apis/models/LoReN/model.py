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
    
    labels = ["fact", "myth", "scam"]
    result = classifier(phrase, labels, hypothesis_template="This statement is a {}.")
    return result['labels'][0].upper()


def evaluate_claim(claim):
    
    phrases = extract_phrases(claim)
    print(f"\nClaim: {claim}\nExtracted phrases: {phrases}")
    
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
    
    return final_verdict, results


if __name__ == "__main__":
    
    final_verdict, results = evaluate_claim("The Eiffel Tower was built in 1889 in Paris")
    print(f"\nFinal verdict: {final_verdict}")
    print("Detailed results:")
    for phrase, classification in results.items():
        print(f" - {phrase}: {classification}")
    