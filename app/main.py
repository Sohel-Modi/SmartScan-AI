# app/main.py (Final version)
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import uvicorn
import os
from app.services.pdf_parser import extract_text_from_pdf, find_github_url
from app.services.github_scraper import get_github_data, find_github_profile_by_name
from app.agents.resume_parser import parse_resume
from app.agents.evaluator import evaluate_candidate

app = FastAPI(
    title="TalentFlow AI",
    description="An AI-powered tool to automate internship or job application screening.",
    version="1.0.0",
)

@app.get("/")
def read_root():
    return {"message": "SamrtScan AI is up and running!"}

@app.post("/screen")
async def screen_candidates(
    job_description: str = Form(...),
    resumes: List[UploadFile] = File(...),
):
    print(f"Received Job Description: {job_description}")

    evaluation_results = []
    for resume in resumes:
        print(f"Processing resume: {resume.filename}")

        # 1. Extract text from PDF
        resume_text = extract_text_from_pdf(resume)
        if not resume_text:
            raise HTTPException(status_code=400, detail=f"Could not extract text from {resume.filename}")

        # 2. Use the agent to parse the resume text
        parsed_resume_data = parse_resume(resume_text)

        # 3. Find GitHub URL
        github_url = find_github_url(resume_text)
        github_username = None
        if github_url:
            github_username = github_url.split('/')[-1]
        else:
            # 4. Fallback: Search for GitHub profile by name
            print(f"No GitHub URL found. Attempting to search for a profile for {parsed_resume_data.get('name')}.")
            profile_url = find_github_profile_by_name(parsed_resume_data.get('name'))
            if profile_url:
                github_username = profile_url.split('/')[-1]

        # 5. Get GitHub data
        github_data = {}
        if github_username:
            github_data = get_github_data(github_username)

        # 6. Evaluate the candidate using the evaluator agent
        evaluation = evaluate_candidate(
            job_description=job_description,
            resume_data=parsed_resume_data,
            github_data=github_data
        )

        evaluation_results.append(evaluation)

    return {
        "status": "screening_complete",
        "results": evaluation_results,
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)