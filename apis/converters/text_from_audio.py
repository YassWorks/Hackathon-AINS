# Audio processing functionality has been disabled for Docker compatibility
# To enable audio processing, install: pip install SpeechRecognition pyaudio
# and uncomment the implementation below

def text_from_audio(audio_path: str) -> str:
    """
    Audio processing is currently disabled to avoid Docker compatibility issues.
    This function returns a message indicating that audio processing is not available.
    
    To enable audio processing:
    1. Install required packages: pip install SpeechRecognition pyaudio
    2. Install system dependencies: apt-get install portaudio19-dev python3-pyaudio
    3. Uncomment the implementation below
    """
    return "Audio processing is currently disabled. Please convert your audio to text manually or use text/image input instead."

# Commented out audio processing implementation:
# 
# import speech_recognition as sr
# 
# def text_from_audio(audio_path: str) -> str:
#     recognizer = sr.Recognizer()
#     try:
#         with sr.AudioFile(audio_path) as source:
#             audio_data = recognizer.record(source)
#             text = recognizer.recognize_google(audio_data)
#             return text.strip()
#     except sr.UnknownValueError:
#         return "Could not understand audio."
#     except sr.RequestError as e:
#         return f"Speech recognition failed: {e}"
#     except Exception as e:
#         return f"An error occurred during audio processing: {e}"