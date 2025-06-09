import spacy
from transformers import pipeline


# nlp = spacy.load("en_core_web_sm")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


# def extract_phrases(claim):
    
#     doc = nlp(claim)
#     phrases = []
#     for token in doc:
#         if token.dep_ in ("nsubj", "ROOT", "dobj", "pobj"):
#             subtree = " ".join([t.text for t in token.subtree])
#             phrases.append(subtree)
#     return list(set(phrases))


def classify_phrase(phrase):
    
    labels = ["FACT", "MYTH", "SCAM"]
    result = classifier(phrase, labels)
    # print("#"*50)
    # print(result)
    # print("#"*50)
    return result['labels'][0].upper()


def evaluate_claim(claim, sources: list[str]):
    
    phrases = [(claim + " Evidence for that is: " + source) for source in sources]
    # sub_phrases = [extract_phrases(phrase) for phrase in phrases]
    
    labels = ["FACT", "MYTH", "SCAM"]
    results = [0, 0, 0]
    
    for phrase in phrases:
        classification = classify_phrase(phrase)
        results[labels.index(classification)] += 1
    
    # for sub_phrase_list in sub_phrases:
    #     for sub_phrase in sub_phrase_list:
    #         print("-"*100)
    #         print(sub_phrase)
    #         print("-"*100)
    #         classification = classify_phrase(sub_phrase)
    #         results[labels.index(classification)] += 1

    print(f"LoReN Results ('FACT', 'MYTH', 'SCAM'): {results}")
    return labels[results.index(max(results))]


# if __name__ == "__main__":
    
#     final_verdict = evaluate_claim("The Eiffel Tower was built in 1889 in Paris")
#     print(f"\nFinal verdict: {final_verdict}")
#     print("Detailed results:")
    