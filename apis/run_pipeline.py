# pipeline/run_pipeline.py

from converters.text_from_audio import text_from_audio
from converters.text_from_image import text_from_image
from converters.text_from_text import text_from_text
from models.NLI.model import avg_predict, reformulate_claim
from web_searcher.app import search_statement

import os

def detect_modality(input_path):
    """
    Detect the modality of the input file based on extension or heuristic.
    """
    ext = os.path.splitext(input_path)[1].lower()
    if ext in [".wav", ".mp3", ".m4a"]:
        return "audio"
    elif ext in [".jpg", ".jpeg", ".png", ".bmp"]:
        return "image"
    elif ext in [".txt"]:
        return "text"
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def run_pipeline(input_path: str, claim: str):
    """
    Run full pipeline:
    1. Detect modality (audio/image/text).
    2. Convert input to text.
    3. Search the web for supporting/rejecting evidence.
    4. Use NLI model to classify claim based on extracted evidence.
    """
    modality = detect_modality(input_path)
    print(f"[INFO] Detected modality: {modality}")

    if modality == "audio":
        base_text = text_from_audio(input_path)
    elif modality == "image":
        base_text = text_from_image(input_path)
    elif modality == "text":
        base_text = text_from_text(input_path)
    else:
        raise RuntimeError("Unknown modality")

    print("\n[INFO] Extracted evidence from file:", base_text)

    # Clean and reformulate claim if needed
    claim = reformulate_claim(claim)
    print(f"[INFO] Reformulated claim: {claim}")

    # Retrieve additional evidence from web
    print("\n[INFO] Searching the web for additional evidence...")
    web_sources = search_statement(claim, num_results=5)
    print(f"[DEBUG] Web sources found: {list(web_sources.keys())}")
    web_evidences = list(web_sources.values())

    if not web_evidences:
        print("[WARNING] No web evidence found. Using only file-based input.")
        evidence_list = [base_text]
    else:
        evidence_list = [base_text] + web_evidences

    # Run NLI prediction
    prediction = avg_predict(claim, evidence_list)
    print(f"\n[PIPELINE RESULT] The claim is classified as: {prediction}")
    return prediction


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python run_pipeline.py <input_file>")
        exit(1)

    input_file = sys.argv[1]
    with open(input_file, "r", encoding="utf-8") as f:
        input_claim = f.read().strip()

    run_pipeline(input_file, input_claim)
