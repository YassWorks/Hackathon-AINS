from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="roberta-large-mnli")

# The first step is to filter out opinions and subjective statements 
# as there's no point in trying to prove or disprove them.
# This is also handy later on when we develop the web extenstion as it will
# limit the overhead and speed up the process.

def is_claim(text):
    result = classifier(text, candidate_labels=["claim", "opinion"])
    if isinstance(result, dict) and "labels" in result:
        return result["labels"][0]  # "claim" or "opinion"
    else:
        raise ValueError("Unexpected result format from classifier")

print(is_claim("I think the Earth is flat."))
print(is_claim("The Moon orbits the Earth."))
print(is_claim("My cat is the best pet to ever exist."))