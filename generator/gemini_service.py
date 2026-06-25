import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

def get_questions(role, difficulty, no_questions, ques_type):

    if ques_type == "mcq":
        prompt = f"""Generate {no_questions} {difficulty} level interview MCQs for {role}.
        Return only valid JSON.
        Format:
        [
        {{
        "question":"What is Python?",
        "options":
        {{
        "A":"Database",
        "B":"Programming Language",
        "C":"Browser",
        "D":"Operating System"
        }},
        "answer":"B",
        "explanation":"Python is a programming language."
        }}
        ]
        """
    else:
        prompt = f""" Generate {no_questions} {difficulty} level interview questions for a {role}.
    Only return numbered questions. 
    Return ONLY valid JSON.

    Format:

    [
    {{
    "question":"What is OOP?",
    "answer":"Object Oriented Programming",
    "explanation":"It helps organize code."
    }}
    ]
    """

    response = model.generate_content(prompt)

    text = response.text

    text = text.replace("```json", "")
    text = text.replace("```", "")

    return json.loads(text)