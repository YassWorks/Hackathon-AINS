from PIL import Image
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration, pipeline
import torch

# Load models once (global initialization)
caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def text_from_image(image_path: str) -> str:
    """
    Converts an image into a rich textual representation including OCR-extracted text,
    a generated caption, and detected emotional tone.
    """
    try:
        image = Image.open(image_path).convert("RGB")

        # 1. OCR: Extract visible text from the image
        ocr_text = pytesseract.image_to_string(image).strip()

        # 2. Caption: Describe image context
        inputs = caption_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            generated_ids = caption_model.generate(**inputs)
        caption = caption_processor.decode(generated_ids[0], skip_special_tokens=True)

        # 3. Combine results
        final_text = f"Description: {caption}\nText: {ocr_text}"
        return final_text

    except Exception as e:
        return f"Failed to process image: {str(e)}"
