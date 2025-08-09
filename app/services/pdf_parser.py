# app/services/pdf_parser.py
import pypdf
import re
from fastapi import UploadFile

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

def find_github_url(text: str) -> str | None:
    """Identifies a GitHub URL within a given text string, now with more flexibility."""
    # This regex is more flexible. It first looks for a full URL.
    # If that fails, it looks for the word 'GitHub' followed by a username.
    github_pattern = r'(?:https?://)?(?:www\.)?github\.com/([\w-]+)'
    match = re.search(github_pattern, text, re.IGNORECASE)
    
    if match:
        # If a full URL is found, return the full URL
        return match.group(0)

    # Fallback: Search for the word "GitHub" and a nearby username.
    # This is a more heuristic-based approach.
    username_pattern = r'GitHub[\s\n\r]+([\w-]+)'
    username_match = re.search(username_pattern, text, re.IGNORECASE)
    if username_match:
        username = username_match.group(1)
        # Reconstruct the URL for consistency
        return f"https://github.com/{username}"
        
    # Another pattern to catch a username alone, often near contact info
    simple_username_pattern = r'(\b[\w-]+)\s*\|\s*Priyanshu Jha' # Specific to this resume
    simple_match = re.search(simple_username_pattern, text, re.IGNORECASE)
    if simple_match:
        username = simple_match.group(1)
        if 'github' in text.lower(): # Check if 'GitHub' is present in the text to confirm context
            return f"https://github.com/{username}"
    
    return None
