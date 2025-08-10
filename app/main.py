# app/main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List
import uvicorn
import os
import json
import uuid
import re
from app.services.github_scraper import get_github_data, find_github_profile_by_name

from app.services.pdf_parser import extract_text_from_pdf, find_github_url_with_llm 
from app.services.github_scraper import get_github_data, find_github_profile_by_name
from app.agents.resume_parser import parse_resume
from app.agents.evaluator import evaluate_candidate

app = FastAPI(
    title="TalentFlow AI",
    description="An AI-powered tool to automate internship application screening.",
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
    
    evaluation_results = []
    
    # Store the job description
    job_description_id = str(uuid.uuid4())
    os.makedirs(f"data_output/{job_description_id}", exist_ok=True)
    with open(f"data_output/{job_description_id}/job_description.json", "w") as f:
        json.dump({"job_description": job_description}, f, indent=4)
    
    for resume in resumes:
        print(f"Processing resume: {resume.filename}")
        candidate_id = str(uuid.uuid4())
        
        # 1. Extract text from PDF
        resume_text = extract_text_from_pdf(resume)
        
        # Data dictionary to store all intermediate steps
        candidate_data = {
            "candidate_id": candidate_id,
            "job_description": job_description,
            "filename": resume.filename,
            "raw_resume_text": resume_text,
            "parsed_resume_data": {},
            "github_data": {},
            "final_evaluation": {}
        }
        
        if not resume_text:
            print(f"Warning: Could not extract text from {resume.filename}. Skipping this candidate.")
            continue
        
        # 2. Use the agent to parse the resume text
        parsed_resume_data = parse_resume(resume_text)
        candidate_data["parsed_resume_data"] = parsed_resume_data

        candidate_name = parsed_resume_data.get('name')
        if not candidate_name:
            parsed_resume_data['name'] = os.path.splitext(resume.filename)[0]
            candidate_name = parsed_resume_data.get('name')
            print(f"Warning: Could not extract a name. Using filename as name: {candidate_name}")

        # 3. Find GitHub URL
        github_url = find_github_url_with_llm(resume_text)
        github_username = None
        if github_url and 'github.com' in github_url:
            github_username = github_url.split('/')[-1]
            print(f"Found GitHub URL for {candidate_name}: {github_url}")
        else:
            # 4. Fallback: Search for GitHub profile by name
            print(f"No GitHub URL found. Attempting to search for a profile for {candidate_name}.")
            profile_url = find_github_profile_by_name(candidate_name)
            if profile_url:
                github_username = profile_url.split('/')[-1]
                print(f"Fallback found profile for {candidate_name}: {profile_url}")
        
        # 5. Get GitHub data
        github_data = {}
        if github_username:
            # --- REFINED FIX: Add a more specific check for invalid usernames ---
            # GitHub usernames can only contain alphanumeric characters and hyphens.
            if not re.match(r'^[a-zA-Z0-9-]+$', github_username):
                print(f"Warning: Extracted username '{github_username}' is not a valid GitHub username. Skipping GitHub API call.")
                github_username = None # Set to None to prevent API call
            else:
                github_data = get_github_data(github_username)

        candidate_data["github_data"] = github_data


         # 6. Evaluate the candidate using the evaluator agent
        evaluation_input = {
            "job_description": job_description,
            "resume_data": parsed_resume_data,
            "github_data": github_data
        }

        # --- NEW: Print the JSON input for debugging ---
        print("\n" + "="*50)
        print("JSON INPUT FOR EVALUATOR AGENT:")
        print(json.dumps(evaluation_input, indent=4))
        print("="*50 + "\n")
        # --------------------------------------------------

        evaluation = evaluate_candidate(
            job_description=job_description,
            resume_data=parsed_resume_data,
            github_data=github_data
        )
        # # 6. Evaluate the candidate using the evaluator agent
        # evaluation = evaluate_candidate(
        #     job_description=job_description,
        #     resume_data=parsed_resume_data,
        #     github_data=github_data
        # )
        
        candidate_data["final_evaluation"] = evaluation
        evaluation_results.append(evaluation)

        # 7. Store all data for this candidate in a JSON file
        with open(f"data_output/{job_description_id}/{candidate_id}.json", "w") as f:
            json.dump(candidate_data, f, indent=4)
    
    if not evaluation_results:
        return {
            "status": "screening_failed",
            "message": "No candidates were successfully screened. Check the server logs for details."
        }

    return {
        "status": "screening_complete",
        "results": evaluation_results,
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# @app.post("/screen")
# async def screen_candidates(
#     job_description: str = Form(...),
#     resumes: List[UploadFile] = File(...),
# ):
#     print(f"Received Job Description: {job_description}")
    
#     evaluation_results = []
    
#     # Store the job description
#     job_description_id = str(uuid.uuid4())
#     os.makedirs(f"data_output/{job_description_id}", exist_ok=True)
#     with open(f"data_output/{job_description_id}/job_description.json", "w") as f:
#         json.dump({"job_description": job_description}, f, indent=4)
    
#     for resume in resumes:
#         print(f"Processing resume: {resume.filename}")
#         candidate_id = str(uuid.uuid4())
        
#         # 1. Extract text from PDF
#         resume_text = extract_text_from_pdf(resume)
        
#         # Data dictionary to store all intermediate steps
#         candidate_data = {
#             "candidate_id": candidate_id,
#             "job_description": job_description,
#             "filename": resume.filename,
#             "raw_resume_text": resume_text,
#             "parsed_resume_data": {},
#             "github_data": {},
#             "final_evaluation": {}
#         }
        
#         if not resume_text:
#             print(f"Warning: Could not extract text from {resume.filename}. Skipping this candidate.")
#             continue
        
#         # 2. Use the agent to parse the resume text
#         parsed_resume_data = parse_resume(resume_text)
#         candidate_data["parsed_resume_data"] = parsed_resume_data

#         candidate_name = parsed_resume_data.get('name')
#         if not candidate_name:
#             parsed_resume_data['name'] = os.path.splitext(resume.filename)[0]
#             candidate_name = parsed_resume_data.get('name')
#             print(f"Warning: Could not extract a name. Using filename as name: {candidate_name}")

#         # 3. Find GitHub URL
#         github_url = find_github_url_with_llm(resume_text)
#         github_username = None
#         if github_url and 'github.com' in github_url:
#             github_username = github_url.split('/')[-1]
#             print(f"Found GitHub URL for {candidate_name}: {github_url}")
#         else:
#             # 4. Fallback: Search for GitHub profile by name
#             print(f"No GitHub URL found. Attempting to search for a profile for {candidate_name}.")
#             profile_url = find_github_profile_by_name(candidate_name)
#             if profile_url:
#                 github_username = profile_url.split('/')[-1]
#                 print(f"Fallback found profile for {candidate_name}: {profile_url}")
        
#         # 5. Get GitHub data
#         github_data = {}
#         if github_username:
#             # --- FIX: Add a simple check to see if the username is likely an email prefix ---
#             if '@' in github_username or '.' in github_username:
#                  print(f"Warning: Extracted username '{github_username}' looks like an email prefix. Skipping GitHub API call.")
#                  github_username = None # Set to None to prevent API call
#             else:
#                 github_data = get_github_data(github_username)

#         candidate_data["github_data"] = github_data

#         # 6. Evaluate the candidate using the evaluator agent
#         evaluation = evaluate_candidate(
#             job_description=job_description,
#             resume_data=parsed_resume_data,
#             github_data=github_data
#         )
        
#         candidate_data["final_evaluation"] = evaluation
#         evaluation_results.append(evaluation)

#         # 7. Store all data for this candidate in a JSON file
#         with open(f"data_output/{job_description_id}/{candidate_id}.json", "w") as f:
#             json.dump(candidate_data, f, indent=4)
    
#     if not evaluation_results:
#         return {
#             "status": "screening_failed",
#             "message": "No candidates were successfully screened. Check the server logs for details."
#         }

#     return {
#         "status": "screening_complete",
#         "results": evaluation_results,
#     }

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# @app.post("/screen")
# async def screen_candidates(
#     job_description: str = Form(...),
#     resumes: List[UploadFile] = File(...),
# ):
#     print(f"Received Job Description: {job_description}")
    
#     evaluation_results = []
    
#     # Store the job description
#     job_description_id = str(uuid.uuid4())
#     os.makedirs(f"data_output/{job_description_id}", exist_ok=True)
#     with open(f"data_output/{job_description_id}/job_description.json", "w") as f:
#         json.dump({"job_description": job_description}, f, indent=4)
    
#     for resume in resumes:
#         print(f"Processing resume: {resume.filename}")
#         candidate_id = str(uuid.uuid4())
        
#         # 1. Extract text from PDF
#         resume_text = extract_text_from_pdf(resume)
        
#         # Data dictionary to store all intermediate steps
#         candidate_data = {
#             "candidate_id": candidate_id,
#             "job_description": job_description,
#             "filename": resume.filename,
#             "raw_resume_text": resume_text,
#             "parsed_resume_data": {},
#             "github_data": {},
#             "final_evaluation": {}
#         }
        
#         if not resume_text:
#             print(f"Warning: Could not extract text from {resume.filename}. Skipping this candidate.")
#             continue
        
#         # 2. Use the agent to parse the resume text
#         parsed_resume_data = parse_resume(resume_text)
#         candidate_data["parsed_resume_data"] = parsed_resume_data

#         candidate_name = parsed_resume_data.get('name')
#         if not candidate_name:
#             parsed_resume_data['name'] = os.path.splitext(resume.filename)[0]
#             candidate_name = parsed_resume_data.get('name')
#             print(f"Warning: Could not extract a name. Using filename as name: {candidate_name}")

#         # 3. Find GitHub URL
#         github_url = find_github_url(resume_text)
#         github_username = None
#         if github_url:
#             github_username = github_url.split('/')[-1]
#             print(f"Found GitHub URL for {candidate_name}: {github_url}")
#         else:
#             # 4. Fallback: Search for GitHub profile by name
#             print(f"No GitHub URL found. Attempting to search for a profile for {candidate_name}.")
#             profile_url = find_github_profile_by_name(candidate_name)
#             if profile_url:
#                 github_username = profile_url.split('/')[-1]
#                 print(f"Fallback found profile for {candidate_name}: {profile_url}")
        
#         # 5. Get GitHub data
#         if github_username:
#             github_data = get_github_data(github_username)
#             candidate_data["github_data"] = github_data

#         # 6. Evaluate the candidate using the evaluator agent
#         evaluation = evaluate_candidate(
#             job_description=job_description,
#             resume_data=parsed_resume_data,
#             github_data=github_data
#         )
        
#         candidate_data["final_evaluation"] = evaluation
#         evaluation_results.append(evaluation)

#         # 7. Store all data for this candidate in a JSON file
#         with open(f"data_output/{job_description_id}/{candidate_id}.json", "w") as f:
#             json.dump(candidate_data, f, indent=4)
    
#     if not evaluation_results:
#         return {
#             "status": "screening_failed",
#             "message": "No candidates were successfully screened. Check the server logs for details."
#         }

#     return {
#         "status": "screening_complete",
#         "results": evaluation_results,
#     }

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)





# # app/main.py
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from typing import List
# import uvicorn
# import os
# from app.services.pdf_parser import extract_text_from_pdf, find_github_url
# from app.services.github_scraper import get_github_data, find_github_profile_by_name
# from app.agents.resume_parser import parse_resume
# from app.agents.evaluator import evaluate_candidate
# import sys

# app = FastAPI(
#     title="TalentFlow AI",
#     description="An AI-powered tool to automate internship application screening.",
#     version="1.0.0",
# )

# @app.get("/")
# def read_root():
#     return {"message": "TalentFlow AI is up and running!"}

# @app.post("/screen")
# async def screen_candidates(
#     job_description: str = Form(...),
#     resumes: List[UploadFile] = File(...),
# ):
#     print(f"Received Job Description: {job_description}")
    
#     evaluation_results = []
#     for resume in resumes:
#         print(f"Processing resume: {resume.filename}")
        
#         # 1. Extract text from PDF
#         resume_text = extract_text_from_pdf(resume)
        
#         # --- DEBUG: Print the raw extracted text to the console ---
#         print("\n" + "="*50)
#         print(f"RAW TEXT EXTRACTED FROM {resume.filename}:")
#         print(resume_text)
#         print("="*50 + "\n")
#         # -----------------------------------------------------------

#         if not resume_text:
#             print(f"Warning: Could not extract text from {resume.filename}. Skipping this candidate.")
#             continue
        
#         # 2. Use the agent to parse the resume text
#         parsed_resume_data = parse_resume(resume_text)

#         candidate_name = parsed_resume_data.get('name')
#         if not candidate_name:
#             # Add a name key with a placeholder if not found, to prevent the `AttributeError` later
#             parsed_resume_data['name'] = os.path.splitext(resume.filename)[0]
#             candidate_name = parsed_resume_data.get('name')
#             print(f"Warning: Could not extract a name from the resume. Using filename as name: {candidate_name}")

#         # 3. Find GitHub URL
#         github_url = find_github_url(resume_text)
#         github_username = None
#         if github_url:
#             github_username = github_url.split('/')[-1]
#             print(f"Found GitHub URL for {candidate_name}: {github_url}")
#         else:
#             # 4. Fallback: Search for GitHub profile by name
#             print(f"No GitHub URL found. Attempting to search for a profile for {candidate_name}.")
#             profile_url = find_github_profile_by_name(candidate_name)
#             if profile_url:
#                 github_username = profile_url.split('/')[-1]
#                 print(f"Fallback found profile for {candidate_name}: {profile_url}")
        
#         # 5. Get GitHub data
#         github_data = {}
#         if github_username:
#             github_data = get_github_data(github_username)

#         # 6. Evaluate the candidate using the evaluator agent
#         evaluation = evaluate_candidate(
#             job_description=job_description,
#             resume_data=parsed_resume_data,
#             github_data=github_data
#         )
        
#         evaluation_results.append(evaluation)
    
#     if not evaluation_results:
#         return {
#             "status": "screening_failed",
#             "message": "No candidates were successfully screened. Check the server logs for details."
#         }

#     return {
#         "status": "screening_complete",
#         "results": evaluation_results,
#     }

# if __name__ == "__main__":
#     uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
