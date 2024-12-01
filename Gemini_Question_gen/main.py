from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
import google.generativeai as genai
import PyPDF2
import os
from pydantic import BaseModel

app = FastAPI()
GPT_MODEL = "gemini-1.5-pro"

genai.configure(api_key="AIzaSyCN8lHHrnwykZQtWRzNsDLjOB6jeLPQkbI")  # Replace with your actual API key

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
async def generate_questions(prompt):
    questions=[]
    try:
        model = genai.GenerativeModel(GPT_MODEL)
        result = model.generate_content(prompt)
        lines= result.text.splitlines()  # Assuming the questions are line-separated
        for line in lines:
            if line.strip().startswith(tuple(str(i) + "." for i in range(1, 6))):
                questions.append(line.strip())
        
        return questions
    except Exception as e:
        print(f"Error generating interview questions: {str(e)}")
        return ["Error generating questions."]

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
