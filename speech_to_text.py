import speech_recognition as sr

def transcribe_audio(file_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Speech was unclear"
    except sr.RequestError:
        return "API unavailable"
