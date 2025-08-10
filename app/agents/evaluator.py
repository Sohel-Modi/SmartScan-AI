# app/agents/evaluator.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the LLM (using the same model as the resume parser)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# --- UPDATED PROMPT: Now includes structured output for strengths and weaknesses ---
template = """
You are an expert technical recruiter. Your task is to evaluate a candidate based on their resume and a deep dive into their GitHub profile. You must provide a score and a detailed explanation in JSON format.

Here is the job description:
---
{job_description}
---

Here is the candidate's resume data (parsed into JSON):
---
{resume_data}
---

Here is the candidate's GitHub profile data (parsed into JSON). Pay close attention to the 'readme_content' and 'recent_commits' for each project to form a holistic view:
---
{github_data}
---

Follow these instructions carefully:
1.  Provide a score from 1 to 10 for the candidate's fit for the role.
2.  The explanation must be structured into two sections: 'strengths' and 'weaknesses'.
3.  List the candidate's key strengths in an array of bullet points, citing specific examples from their resume (e.g., project names, skills) and GitHub profile (e.g., repository names, languages used, stars) to justify their score.
4.  List the candidate's key weaknesses in an array of bullet points, explaining any gaps in their experience or skills relative to the job description.
5.  If no GitHub data is available, mention that in the weaknesses section.
6.  The output MUST be a single, valid JSON object, and NOTHING else. Do not include any text, conversation, or markdown code blocks outside the JSON.

Expected JSON Format:
{{
    "candidate_name": "Full Name",
    "score": 8,
    "explanation": {{
        "strengths": [
            "Strength 1 (e.g., 'Strong Python skills as demonstrated in project X')",
            "Strength 2 (e.g., 'Experience with PyTorch, a key requirement')"
        ],
        "weaknesses": [
            "Weakness 1 (e.g., 'Lack of experience in Natural Language Processing')",
            "Weakness 2 (e.g., 'GitHub profile is not well-documented')"
        ]
    }}
}}
"""

prompt = PromptTemplate(
    input_variables=["job_description", "resume_data", "github_data"],
    template=template
)

def evaluate_candidate(job_description: str, resume_data: dict, github_data: dict) -> dict:
    """
    Evaluates a candidate based on multiple data sources and provides a score and explanation.
    """
    chain = prompt | llm
    
    # Prepare the input for the chain
    input_data = {
        "job_description": job_description,
        "resume_data": str(resume_data),
        "github_data": str(github_data)
    }
    
    try:
        response = chain.invoke(input_data)
        
        # FIX: Clean the LLM response before parsing
        clean_response = response.content.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]

        return json.loads(clean_response)
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from LLM: {e}")
        print(f"LLM response was: {response.content}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred in LLM invocation: {e}")
        return {}


# # app/agents/evaluator.py
# import os
# import json
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Initialize the LLM (using the same model as the resume parser)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# # The prompt template is the "secret sauce" of this project
# template = """
# You are an expert technical recruiter. Your task is to evaluate a candidate based on their resume and GitHub profile against a specific job description. You must provide a score and a detailed explanation in JSON format.

# Here is the job description:
# ---
# {job_description}
# ---

# Here is the candidate's resume data (parsed into JSON):
# ---
# {resume_data}
# ---

# Here is the candidate's GitHub profile data (parsed into JSON):
# ---
# {github_data}
# ---

# Follow these instructions carefully:
# 1.  Provide a score from 1 to 10 for the candidate's fit for the role.
# 2.  Write a detailed, human-readable explanation for the score. The explanation must be concise but include specific examples from their resume (e.g., project names, skills) and GitHub profile (e.g., repository names, languages used, stars) to justify the score.
# 3.  If no GitHub data is available, mention that in your explanation and base your evaluation solely on the resume.
# 4.  The output MUST be a single, valid JSON object, and NOTHING else. Do not include any text, conversation, or markdown code blocks outside the JSON.

# Expected JSON Format:
# {{
#     "candidate_name": "Full Name",
#     "score": 8,
#     "explanation": "Based on their experience with..."
# }}
# """

# prompt = PromptTemplate(
#     input_variables=["job_description", "resume_data", "github_data"],
#     template=template
# )

# def evaluate_candidate(job_description: str, resume_data: dict, github_data: dict) -> dict:
#     """
#     Evaluates a candidate based on multiple data sources and provides a score and explanation.
#     """
#     chain = prompt | llm
    
#     # Prepare the input for the chain
#     input_data = {
#         "job_description": job_description,
#         "resume_data": str(resume_data),
#         "github_data": str(github_data)
#     }
    
#     try:
#         response = chain.invoke(input_data)
        
#         # FIX: Clean the LLM response before parsing
#         clean_response = response.content.strip()
#         if clean_response.startswith("```json"):
#             clean_response = clean_response[7:]
#         if clean_response.endswith("```"):
#             clean_response = clean_response[:-3]

#         return json.loads(clean_response)
    
#     except json.JSONDecodeError as e:
#         print(f"Error parsing JSON from LLM: {e}")
#         print(f"LLM response was: {response.content}")
#         return {}
#     except Exception as e:
#         print(f"An unexpected error occurred in LLM invocation: {e}")
#         return {}


# # app/agents/evaluator.py
# import os
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Initialize the LLM (using the same model as the resume parser)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# # The prompt template is the "secret sauce" of this project
# template = """
# You are an expert technical recruiter. Your task is to evaluate a candidate based on their resume and GitHub profile against a specific job description. You must provide a score and a detailed explanation in JSON format.

# Here is the job description:
# ---
# {job_description}
# ---

# Here is the candidate's resume data (parsed into JSON):
# ---
# {resume_data}
# ---

# Here is the candidate's GitHub profile data (parsed into JSON):
# ---
# {github_data}
# ---

# Follow these instructions carefully:
# 1.  Provide a score from 1 to 10 for the candidate's fit for the role.
# 2.  Write a detailed, human-readable explanation for the score. The explanation must be concise but include specific examples from their resume (e.g., project names, skills) and GitHub profile (e.g., repository names, languages used, stars) to justify the score.
# 3.  If no GitHub data is available, mention that in your explanation and base your evaluation solely on the resume.
# 4.  Ensure the output is a single, valid JSON object.

# Expected JSON Format:
# {{
#     "candidate_name": "Full Name",
#     "score": 8,
#     "explanation": "Based on their experience with..."
# }}
# """

# prompt = PromptTemplate(
#     input_variables=["job_description", "resume_data", "github_data"],
#     template=template
# )

# import json

# # Define the evaluation function
# def evaluate_candidate(job_description: str, resume_data: dict, github_data: dict) -> dict:
#     """
#     Evaluates a candidate based on multiple data sources and provides a score and explanation.
#     """
#     chain = prompt | llm
    
#     # Prepare the input for the chain
#     input_data = {
#         "job_description": job_description,
#         "resume_data": str(resume_data), # Convert to string for the prompt
#         "github_data": str(github_data)  # Convert to string for the prompt
#     }
    
#     try:
#         response = chain.invoke(input_data)
        
#         # --- FIX: Clean the LLM response before parsing ---
#         clean_response = response.content.strip()
#         if clean_response.startswith("```json"):
#             clean_response = clean_response[7:]
#         if clean_response.endswith("```"):
#             clean_response = clean_response[:-3]

#         return json.loads(clean_response)
    
#     except json.JSONDecodeError as e:
#         print(f"Error parsing JSON from LLM: {e}")
#         print(f"LLM response was: {response.content}")
#         return {}
#     except Exception as e:
#         print(f"An unexpected error occurred in LLM invocation: {e}")
#         return {}



# def evaluate_candidate(job_description: str, resume_data: dict, github_data: dict) -> dict:
#     """
#     Evaluates a candidate based on multiple data sources and provides a score and explanation.
#     """
#     chain = prompt | llm

#     # Prepare the input for the chain
#     input_data = {
#         "job_description": job_description,
#         "resume_data": str(resume_data), # Convert to string for the prompt
#         "github_data": str(github_data)  # Convert to string for the prompt
#     }

#     response = chain.invoke(input_data)

#     try:
#         import json
#         return json.loads(response.content)
#     except json.JSONDecodeError as e:
#         print(f"Error parsing JSON from LLM: {e}")
#         return {"error": "Could not parse JSON from LLM response."} 
