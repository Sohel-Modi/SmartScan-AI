# app/agents/resume_parser.py
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define the prompt template for resume parsing
template = """
You are an expert resume parser. Your task is to extract the following information from the raw text of a resume and structure it into a JSON object.

The resume text is provided below.

Resume Text:
---
{resume_text}
---

Follow these rules:
- Extract the candidate's full name.
- List all skills in an array (e.g., ["Python", "Machine Learning"]).
- Identify and list all projects with their descriptions.
- Extract all professional experience entries, including company name, title, and duration.
- Extract all educational qualifications, including degree, university, and year.
- Ensure the output is a single, valid JSON object.

Expected JSON Format:
{{
    "name": "Full Name",
    "email": "email@example.com",
    "phone": "123-456-7890",
    "github_url": "https://github.com/username",
    "skills": [ "Skill1", "Skill2" ],
    "experience": [
        {{
            "company": "Company A",
            "title": "Job Title",
            "duration": "Start Date - End Date"
        }}
    ],
    "projects": [
        {{
            "name": "Project Name",
            "description": "Project Description"
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "university": "University Name",
            "year": "Graduation Year"
        }}
    ]
}}
"""

prompt = PromptTemplate(
    input_variables=["resume_text"],
    template=template
)

def parse_resume(resume_text: str) -> dict:
    """
    Parses a resume's text and returns a structured JSON object.
    """
    chain = prompt | llm
    response = chain.invoke({"resume_text": resume_text})

    # The LLM output is a string, so we need to parse it as JSON
    try:
        import json
        return json.loads(response.content)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM: {e}")
        return {"error": "Could not parse JSON from LLM response."} 
