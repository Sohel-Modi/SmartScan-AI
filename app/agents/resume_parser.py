# app/agents/resume_parser.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
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
- If a piece of information is not available, use null or an empty array.
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
    # If no text is extracted, return an empty dictionary immediately.
    if not resume_text:
        return {}

    chain = prompt | llm
    
    try:
        # Invoke the LLM with the resume text.
        response = chain.invoke({"resume_text": resume_text})
        
        # --- FIX: Clean the LLM response before parsing ---
        clean_response = response.content.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        # Now try to parse the cleaned response.
        return json.loads(clean_response)

    except json.JSONDecodeError as e:
        # If the LLM returns non-JSON text, gracefully return an empty dict.
        print(f"Error parsing JSON from LLM: {e}")
        print(f"LLM response was: {response.content}")
        return {}
    except Exception as e:
        # Catch any other unexpected errors and return an empty dict.
        print(f"An unexpected error occurred in LLM invocation: {e}")
        return {}


# def parse_resume(resume_text: str) -> dict:
#     """
#     Parses a resume's text and returns a structured JSON object.
#     """
#     # If no text is extracted, return an empty dictionary immediately.
#     if not resume_text:
#         return {}

#     chain = prompt | llm
    
#     try:
#         # Invoke the LLM with the resume text.
#         response = chain.invoke({"resume_text": resume_text})
        
#         # Parse the content of the LLM's response as JSON.
#         # This is where the error was happening.
#         return json.loads(response.content)

#     except json.JSONDecodeError as e:
#         # If the LLM returns non-JSON text, gracefully return an empty dict.
#         print(f"Error parsing JSON from LLM: {e}")
#         print(f"LLM response was: {response.content}")
#         return {}
#     except Exception as e:
#         # Catch any other unexpected errors and return an empty dict.
#         print(f"An unexpected error occurred in LLM invocation: {e}")
#         return {}

