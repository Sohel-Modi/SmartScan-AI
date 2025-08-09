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
    """Identifies a GitHub URL within a given text string."""
    github_pattern = r'https?://(?:www\.)?github\.com/[\w-]+/?'
    match = re.search(github_pattern, text, re.IGNORECASE)
    return match.group(0) if match else None 
