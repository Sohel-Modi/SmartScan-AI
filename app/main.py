# app/main.py
from fastapi import FastAPI, UploadFile, File, Form
from typing import List
import uvicorn

app = FastAPI(
    title="TalentFlow AI",
    description="An AI-powered tool to automate internship/Job application screening.",
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
        candidates_data.append({"filename": resume.filename, "status": "pending"})

    return {
        "status": "processing",
        "job_description": job_description,
        "candidates": candidates_data,
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 
