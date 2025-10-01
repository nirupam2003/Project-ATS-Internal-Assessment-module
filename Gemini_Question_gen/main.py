from fastapi import FastAPI, File, UploadFile, Request,Form
from fastapi.responses import HTMLResponse
import speech_recognition as sr
from pydub import AudioSegment
import google.generativeai as genai
import PyPDF2
import os
from dotenv import load_dotenv
from pydantic import BaseModel


#loading dotnet env
load_dotenv()
app = FastAPI()
GPT_MODEL = "gemini-1.5-pro-002"
genai.configure(api_key=os.environ.get("GEM_API"))  # Replace with your actual API key

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def index():
    return HTMLResponse(content=open("./template/chat.html").read(), status_code=200)


@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Check file type and extract text from PDF
    if file.content_type != 'application/pdf':
        return {"error": "Invalid file type. Please upload a PDF"}

    jd_text = await extract_text(file)
    diff_level="7"
    if not jd_text:
        return {"error": "Failed to extract text from the PDF"}

    # Generate questions based on JD
    with open("prompt.txt", "r") as file:
        prompt_template = file.read()
        # Step 2: Replace the placeholder {jd_text} with the actual job description
        final_prompt = prompt_template.replace("{jd_text}", jd_text).replace("{difficulty_level}",diff_level)
        print(final_prompt)
    questions = await generate_questions(final_prompt)
    print("questions:",questions)
    return {"questions": questions}

@app.post("/chat/")
async def chat(chat_request: ChatRequest):
    # Pass the user's message to Google Generative AI and return the response
    user_message = chat_request.message
    response_text = await get_chat_response(user_message)
    return {"response": response_text}

# Function to extract text from PDF
async def extract_text(pdf_file: UploadFile):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None
    
# Function to generate interview questions based on JD text
question_id=0

async def generate_questions(prompt):
    global question_answer_len
    global question_answers
    question_answers=[]
    question_id=0
    try:
        model = genai.GenerativeModel(GPT_MODEL)
        result = model.generate_content(prompt)
        lines= result.text.splitlines()  # Assuming the questions are line-separated
        for line in lines:
            
            if line.strip().startswith(tuple(str(i) + "." for i in range(1, 6))):
                question_answers.append({"id": question_id, "question": line.strip(),"answer":""})
                question_id += 1
        question_answer_len=len(question_answers)
        return question_answers
    
    except Exception as e:
        print(f"Error generating interview questions: {str(e)}")
        return ["Error generating questions."]
async def verify_answers():
    with open("verify_answers.txt", "a+") as file:
        for pair in question_answers:
            question = pair["question"]
            answer = pair["answer"]
            print("question:", question, '||', "answer:", answer)
            
            # Writing each question-answer pair to the file
            file.write(f"question: {question} || answer: {answer}\n")

    

@app.post("/upload_audio/")
async def upload_audio(audio: UploadFile = File(...),
                       question_id: int = Form(...)):
    # Save the uploaded audio file
    print(question_id)
    audio_filename = "uploaded_audio" + audio.filename
    with open(audio_filename, "wb") as f:
        f.write(await audio.read())
    
    # Convert the file to WAV if it's not already in WAV format
    if not audio_filename.endswith(".wav"):
        audio = AudioSegment.from_file(audio_filename)
        audio.export("uploaded_audio.wav", format="wav")
        audio_filename = "uploaded_audio.wav"

    # Process the audio file with speech recognition
    try:
        with sr.AudioFile(audio_filename) as source:
            recognizer = sr.Recognizer()
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            
           
            if question_id<question_answer_len:
                question_answers[question_id]["answer"]=text
            next_question_id = question_id + 1 if question_id + 1 < question_answer_len else None

             # Check if all answers are completed
            all_answered = all(pair["answer"] for pair in question_answers)
            if all_answered:
                await verify_answers()  # Call `verify_answers()` only when all questions are answered
            
            return {
                "transcription": text,
                "next_question_id": next_question_id
            }
    except Exception as e:
        return {"error": str(e)}

    # Return a response
    
# Function to generate a chat response from user input
async def get_chat_response(user_message):
    try:
        prompt = f"You are an interviewer chatbot. Respond to this message:\n{user_message}"
        model = genai.GenerativeModel(GPT_MODEL)
        result = model.generate_content(prompt)
        return result.text  # Adjust based on the library's response structure
    except Exception as e:
        print(f"Error in chat response: {str(e)}")
        return "Error generating chat response."

