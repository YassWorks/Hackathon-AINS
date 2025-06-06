from helpers.utils import is_claim
from models.NLI.model import avg_predict
from web_searcher.app import search_topic

statement = input("give ur stupid statement: ")
if is_claim(statement) != "claim":
    raise ValueError("The statement is not a claim, please provide a valid claim.")

sources = search_topic(statement, num_paragraphs=20)

result = avg_predict(statement, sources)

print("\n\n" + "="*50)
print(f"The claim '{statement}' is classified as: {result}")
print("="*50 + "\n")