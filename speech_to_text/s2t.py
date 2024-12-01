import speech_recognition as sr

def record_audio():
    """Records audio from the microphone and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak:")
        try:
            # Adjust for ambient noise and record audio
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
            print("Recognizing speech...")
            text = recognizer.recognize_google(audio)  # Using Google Speech-to-Text
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech-to-Text; {e}")
    return None

if __name__ == "__main__":
    text_output = record_audio()
    if text_output:
        print(f"Final Transcription: {text_output}")
    else:
        print("No valid speech detected.")
