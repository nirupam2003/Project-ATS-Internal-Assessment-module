import os
from dotenv import load_dotenv
import speech_recognition as sr
from groq import Groq

# Load environment variables from .env file
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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
            print(f"Could not request results; {e}")
    return None

def query_groq(prompt):
    """Sends a prompt to the Groq API and streams the response."""
    try:
        completion = client.chat.completions.create(
            model="llama3-8b-8192",  # Specify the model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        print("\nGroq Response:")
        for chunk in completion:
            print(chunk.choices[0].delta.content or "", end="")
        print()  # Ensure the output ends with a newline
    except Exception as e:
        print(f"Error querying Groq API: {e}")

def main():
    # Step 1: Record audio and convert to text
    user_input = record_audio()
    if not user_input:
        print("No input detected. Exiting.")
        return

    # Step 2: Query the Groq API with the input text
    print("Querying Groq API...")
    query_groq(user_input)

if __name__ == "__main__":
    main()
