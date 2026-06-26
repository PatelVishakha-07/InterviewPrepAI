import os
from dotenv import load_dotenv
from google import genai
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def get_questions(role, difficulty, no_questions, ques_type):

    if ques_type == "mcq":
        prompt = f"""Generate {no_questions} {difficulty} level interview MCQs for {role}.
Return ONLY valid JSON, no explanation, no markdown.
Format:
[
{{
"question": "What is Python?",
"options": {{
"A": "Database",
"B": "Programming Language",
"C": "Browser",
"D": "Operating System"
}},
"answer": "B",
"explanation": "Python is a programming language."
}}
]"""

    else:
        prompt = f"""Generate {no_questions} {difficulty} level interview questions for a {role}.
Return ONLY valid JSON, no explanation, no markdown.
Format:
[
{{
"question": "What is OOP?",
"answer": "Object Oriented Programming is a paradigm that organizes code into objects.",
"explanation": "It helps organize and reuse code through classes and objects."
}}
]"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
        text = text.rsplit("```", 1)[0]

    return json.loads(text.strip())