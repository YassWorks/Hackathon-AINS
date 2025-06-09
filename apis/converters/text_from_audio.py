import speech_recognition as sr

def text_from_audio(audio_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text.strip()
        except sr.UnknownValueError:
            return "Could not understand audio."
        except sr.RequestError as e:
            return f"Speech recognition failed: {e}"
        except Exception as e:
            return f"An error occurred: {e}"