# app/main.py (updated)
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import uvicorn
import os
from app.services.pdf_parser import extract_text_from_pdf, find_github_url
from app.agents.resume_parser import parse_resume

app = FastAPI(
    title="TalentFlow AI",
    description="An AI-powered tool to automate internship or job application screening.",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "TalentFlow AI is up and running!"}

@app.post("/screen")
async def screen_candidates(
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
):
    print(f"Received Job Description: {job_description}")

    candidates_data = []
    for resume in resumes:
        print(f"Processing resume: {resume.filename}")

        # Extract text from PDF
        resume_text = extract_text_from_pdf(resume)

        # Use the agent to parse the resume text
        parsed_resume_data = parse_resume(resume_text)

        # Find GitHub URL using the regex function (a hybrid approach)
        parsed_resume_data["github_url"] = find_github_url(resume_text)

        candidates_data.append(parsed_resume_data)

    return {
        "status": "resumes_parsed",
        "job_description": job_description,
        "candidates": candidates_data,
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)