from googletrans import Translator
import os
import asyncio # Import asyncio

# Initialize googletrans Translator
try:
    translator = Translator()
except Exception as e:
    print(f"Error initializing googletrans Translator: {e}")
    translator = None

async def translate_to_english(text: str, source_language: str) -> str: # Make function async
    """
    Translates text from French, Arabic, Tunisian Arabic, or transliterated Arabic to English
    using the googletrans library.

    Args:
        text: The text to translate.
        source_language: The source language of the text.
                         Supported values: "fr", "ar", "tunisian_ar", "transliterated_ar"

    Returns:
        The translated text in English, or an error message.
    """
    if not translator:
        return "googletrans Translator not initialized."

    # Map our internal language codes to what googletrans expects (if needed)
    # googletrans generally auto-detects source language well.
    # Forcing source language can sometimes be beneficial.
    lang_map = {
        "fr": "fr",
        "ar": "ar",
        "tunisian_ar": "ar",  # Treat Tunisian as Arabic for googletrans
        "transliterated_ar": "ar" # Treat transliterated as Arabic, googletrans might handle it
    }
    src_lang = lang_map.get(source_language, source_language) # Default to passed lang if not in map

    try:
        # With googletrans, you can specify src and dest, or let it auto-detect src.
        # Forcing 'ar' for Tunisian and transliterated Arabic.
        if source_language in ["tunisian_ar", "transliterated_ar"]:
            # Forcing source might be better for these cases if auto-detection is not robust
            translation = await translator.translate(text, src='ar', dest='en') # Add await
        elif source_language in ["fr", "ar"]:
            translation = await translator.translate(text, src=src_lang, dest='en') # Add await
        else:
            # For any other specified source_language or if we want to rely on auto-detection more broadly
            # However, our defined interface expects specific source languages.
            # This path is less likely given the current design.
            translation = await translator.translate(text, dest='en') # Add await
        
        return translation.text
    except Exception as e:
        return f"Error during googletrans translation: {e}"

async def main_async(): # Create an async main function
    print("Attempting translation using googletrans library...")

    french_text = "Bonjour le monde"
    arabic_text = "مرحبا بالعالم"
    tunisian_text = "Ahla bik fi tounes"
    transliterated_arabic_text = "Marhaba bik"
    complex_transliterated = "Choufli hal"

    print(f"French to English (googletrans): {await translate_to_english(french_text, 'fr')}")
    print(f"Arabic to English (googletrans): {await translate_to_english(arabic_text, 'ar')}")
    print(f"Tunisian Arabic to English (googletrans, as \'ar\'): {await translate_to_english(tunisian_text, 'tunisian_ar')}")
    print(f"Transliterated Arabic to English (googletrans, as \'ar\'): {await translate_to_english(transliterated_arabic_text, 'transliterated_ar')}")
    print(f"Complex Transliterated Arabic to English (googletrans, as \'ar\'): {await translate_to_english(complex_transliterated, 'transliterated_ar')}")

    # Example of letting googletrans auto-detect source language
    # try:
    #     print("\\nTesting auto-detection with transliterated text (googletrans):")
    #     # Ensure translator object is available in this scope if you uncomment
    #     auto_detect_translation = await translator.translate("Choufli hal", dest="en")
    #     detected_lang = auto_detect_translation.src
    #     translated_text = auto_detect_translation.text
    #     print(f"Text: 'Choufli hal' -> Detected: {detected_lang} -> Translated: {translated_text}")
    # except Exception as e:
    #     print(f"Error during auto-detect translation with googletrans: {e}")

if __name__ == '__main__':
    asyncio.run(main_async()) # Run the async main function