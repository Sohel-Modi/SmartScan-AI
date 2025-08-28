# app/services/pdf_parser.py
#----- New code using LLM only for GitHub URL extraction -----
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
    Identifies a GitHub URL within a given text string by relying on the LLM.
    """
    prompt_template = """
    From the following text, find and extract the candidate's GitHub profile URL. 
    The URL might be written as a full link (e.g., https://github.com/username), a shortened URL, or just a username.
    
    Follow these rules strictly:
    - Only extract a username if it is clearly associated with the word 'GitHub' or a URL.
    - If you find a full URL, provide it as is.
    - If you only find a username (e.g., 'Sohel Modi'), return the reconstructed URL (e.g., 'https://github.com/Sohel-Modi').
    - If you see a username with strange characters (e.g., '/gtbpriyanshujhaa'), return the cleaned version ('https://github.com/priyanshujhaa').
    - If you cannot find a GitHub URL or username, return 'null'.

    Resume Text:
    ---
    {resume_text}
    ---

    Your response:
    """
    
    prompt = PromptTemplate(input_variables=["resume_text"], template=prompt_template)
    chain = prompt | llm

    try:
        response = chain.invoke({"resume_text": text})
        url = response.content.strip()
        
        if url.lower() == 'null':
            return None
        return url
        
    except Exception as e:
        print(f"Error invoking LLM for URL extraction: {e}")
        return None

#------- Old code using regex expression + LLM for validation -------
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
#     Identifies a GitHub URL within a given text string using a hybrid LLM and regex approach.
#     """
#     # 1. Use a flexible regex to find any string that looks like a GitHub URL or username.
#     # This is more reliable than asking the LLM to find it from scratch.
#     github_pattern = r'github\.com/[\w-]+|priyanshujhaa|sohel\smodi'
#     match = re.search(github_pattern, text, re.IGNORECASE)
    
#     potential_url_text = match.group(0) if match else "None"

#     # 2. Use a specific prompt to instruct the LLM to validate and clean the text.
#     prompt_template = """
#     A candidate's resume text was scanned, and the following potential GitHub profile string was extracted:
#     '{potential_url_text}'

#     Your task is to either:
#     1. Reconstruct a clean, full GitHub URL from this string.
#     2. If the string is 'None' or does not contain a valid username, return 'null'.

#     Follow these rules strictly:
#     - The output MUST be a full URL in the format 'https://github.com/username'.
#     - The username can only contain alphanumeric characters and hyphens.
#     - If the input is messy (e.g., 'github.com/in/Sohel Modi'), you must extract and use only the valid username ('Sohel-Modi').

#     Example Output 1: https://github.com/priyanshujhaa
#     Example Output 2: https://github.com/Sohel-Modi
#     Example Output 3: null

#     Your response:
#     """
    
#     prompt = PromptTemplate(input_variables=["potential_url_text"], template=prompt_template)
#     chain = prompt | llm

#     try:
#         response = chain.invoke({"potential_url_text": potential_url_text})
#         url = response.content.strip()
        
#         if url.lower() == 'null':
#             return None
#         return url
        
#     except Exception as e:
#         print(f"Error invoking LLM for URL extraction: {e}")
#         return None



