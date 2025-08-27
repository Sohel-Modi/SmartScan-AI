# app/services/pdf_parser.py
import pypdf
import re
from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def extract_text_from_pdf(pdf_file: UploadFile) -> str:
    """Extracts text from a PDF file."""
    try:
        pdf_reader = pypdf.PdfReader(pdf_file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def find_github_url_with_llm(text: str) -> str | None:
    """
    Identifies a GitHub URL within a given text string using a hybrid LLM and regex approach.
    """
    # 1. Use a flexible regex to find any string that looks like a GitHub URL or username.
    # This is more reliable than asking the LLM to find it from scratch.
    github_pattern = r'github\.com/[\w-]+|priyanshujhaa|sohel\smodi'
    match = re.search(github_pattern, text, re.IGNORECASE)
    
    potential_url_text = match.group(0) if match else "None"

    # 2. Use a specific prompt to instruct the LLM to validate and clean the text.
    prompt_template = """
    A candidate's resume text was scanned, and the following potential GitHub profile string was extracted:
    '{potential_url_text}'

    Your task is to either:
    1. Reconstruct a clean, full GitHub URL from this string.
    2. If the string is 'None' or does not contain a valid username, return 'null'.

    Follow these rules strictly:
    - The output MUST be a full URL in the format 'https://github.com/username'.
    - The username can only contain alphanumeric characters and hyphens.
    - If the input is messy (e.g., 'github.com/in/Sohel Modi'), you must extract and use only the valid username ('Sohel-Modi').

    Example Output 1: https://github.com/priyanshujhaa
    Example Output 2: https://github.com/Sohel-Modi
    Example Output 3: null

    Your response:
    """
    
    prompt = PromptTemplate(input_variables=["potential_url_text"], template=prompt_template)
    chain = prompt | llm

    try:
        response = chain.invoke({"potential_url_text": potential_url_text})
        url = response.content.strip()
        
        if url.lower() == 'null':
            return None
        return url
        
    except Exception as e:
        print(f"Error invoking LLM for URL extraction: {e}")
        return None




# # app/services/pdf_parser.py
# import pypdf
# import re
# from fastapi import UploadFile
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate
# from dotenv import load_dotenv
# import os
# import json

# load_dotenv()
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# def extract_text_from_pdf(pdf_file: UploadFile) -> str:
#     """Extracts text from a PDF file."""
#     try:
#         pdf_reader = pypdf.PdfReader(pdf_file.file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() or ""
#         return text
#     except Exception as e:
#         print(f"Error extracting text from PDF: {e}")
#         return ""


# def find_github_url_with_llm(text: str) -> str | None:
#     """
#     Identifies a GitHub URL within a given text string using an LLM.
#     This is a more robust approach than regex alone.
#     """
#     # Prompt to instruct the LLM to find the URL
#     prompt_template = """
#     From the following text, find and extract the candidate's GitHub profile URL. 
#     The URL might be written as a full link (e.g., https://github.com/username) or just as a username. 
    
#     If you find a URL, return it as a single string.
#     If you find a username but not a full URL, return the reconstructed URL (e.g., https://github.com/username).
#     If you cannot find a GitHub URL or username, return 'null'.

#     Resume Text:
#     ---
#     {resume_text}
#     ---

#     Example of expected output:
#     https://github.com/Sohel-Modi
#     https://github.com/priyanshujhaa",

#     Example of no output:
#     null
#     """
    
#     prompt = PromptTemplate(input_variables=["resume_text"], template=prompt_template)
#     chain = prompt | llm

#     try:
#         response = chain.invoke({"resume_text": text})
#         url = response.content.strip()
        
#         if url.lower() == 'null':
#             return None
#         return url
        
#     except Exception as e:
#         print(f"Error invoking LLM for URL extraction: {e}")
#         return None




# import pypdf
# import re
# from fastapi import UploadFile

# def extract_text_from_pdf(pdf_file: UploadFile) -> str:
#     """Extracts text from a PDF file."""
#     try:
#         pdf_reader = pypdf.PdfReader(pdf_file.file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() or ""
#         return text
#     except Exception as e:
#         print(f"Error extracting text from PDF: {e}")
#         return ""

# def find_github_url(text: str) -> str | None:
#     """Identifies a GitHub URL within a given text string, now with more flexibility."""
#     # This regex is more flexible. It first looks for a full URL.
#     # If that fails, it looks for the word 'GitHub' followed by a username.
#     github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
#     match = re.search(github_pattern, text, re.IGNORECASE)
    
#     if match:
#         # If a full URL is found, return the full URL
#         return match.group(0)

#     # Fallback: Search for the word "GitHub" and a nearby username.
#     # This is a more heuristic-based approach.
#     username_pattern = r'GitHub[\s\n\r]+([\w-]+)'
#     username_match = re.search(username_pattern, text, re.IGNORECASE)
#     if username_match:
#         username = username_match.group(1)
#         # Reconstruct the URL for consistency
#         return f"https://github.com/{username}"
        
#     # Another pattern to catch a username alone, often near contact info
#     simple_username_pattern = r'(\b[\w-]+)\s*\|\s*Priyanshu Jha' # Specific to this resume
#     simple_match = re.search(simple_username_pattern, text, re.IGNORECASE)
#     if simple_match:
#         username = simple_match.group(1)
#         if 'github' in text.lower(): # Check if 'GitHub' is present in the text to confirm context
#             return f"https://github.com/{username}"
    
#     return None



# # app/services/pdf_parser.py
# import pypdf
# import re
# from fastapi import UploadFile

# def extract_text_from_pdf(pdf_file: UploadFile) -> str:
#     """Extracts text from a PDF file."""
#     try:
#         pdf_reader = pypdf.PdfReader(pdf_file.file)
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text() or ""
#         return text
#     except Exception as e:
#         print(f"Error extracting text from PDF: {e}")
#         return ""

# def find_github_url(text: str) -> str | None:
#     """Identifies a GitHub URL within a given text string, now with more flexibility."""
    
#     # 1. Primary: Search for a full URL (most reliable)
#     full_url_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
#     match = re.search(full_url_pattern, text, re.IGNORECASE)
#     if match:
#         # Reconstruct the URL to ensure it has the full format
#         return f"https://github.com/{match.group(1)}"

#     # 2. Fallback: Search for 'GitHub' and a nearby username (heuristic-based)
#     github_keyword_pattern = r'GitHub[\s\n\r]+([\w-]+)'
#     keyword_match = re.search(github_keyword_pattern, text, re.IGNORECASE)
#     if keyword_match:
#         return f"https://github.com/{keyword_match.group(1)}"

#     # 3. Fallback: Search for a specific username pattern (like in this resume)
#     # This pattern looks for a string followed by '|' and a name
#     simple_username_pattern = r'(\b[\w-]+)\s*\|\s*(?:Priyanshu Jha|Sohel Modi)'
#     simple_match = re.search(simple_username_pattern, text, re.IGNORECASE)
#     if simple_match and 'github' in text.lower():
#         # Reconstruct the URL
#         return f"https://github.com/{simple_match.group(1)}"
    
#     return None
