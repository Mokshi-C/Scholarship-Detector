import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)

def ask_scholarbot(question, scholarship_context, student_context=""):

    prompt = f"""
You are ScholarBot.

Speak naturally like a helpful scholarship counselor.

Do NOT repeat the entire student profile unless asked.

Keep answers short.

Use bullet points when recommending scholarships.

Student Profile:
{student_context}

Scholarships:
{scholarship_context}

Question:
{question}
You must explain recommendations using:
- income
- marks
- category
- gender
- eligibility score

"""

    response = model.generate_content(prompt)

    return response.text