# streamlit_app.py
import streamlit as st
import requests
import json
import time
import os

st.set_page_config(page_title="SmartScan", page_icon="🔍")

# Title and description
st.title("SmartScan: AI Internship Screener Agent")
st.write("An AI-powered tool to screen internship applications based on resumes and GitHub profiles.")

# File uploader and job description input
st.markdown("---")
job_description = st.text_area("Job Description", height=200)
resume_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)

# Define the FastAPI endpoint
FASTAPI_URL = "http://127.0.0.1:8000/screen"

if st.button("Screen Candidates"):
    if not job_description:
        st.error("Please provide a job description.")
    elif not resume_files:
        st.error("Please upload at least one resume.")
    else:
        # The spinner will be shown, but the log messages are removed.
        with st.spinner("Screening in progress..."):
            files = [('resumes', resume) for resume in resume_files]
            data = {'job_description': job_description}

            try:
                response = requests.post(FASTAPI_URL, files=files, data=data)

                if response.status_code == 200:
                    results = response.json().get("results", [])
                    st.success("Screening complete!")
                    st.markdown("---")

                    # --- Correctly calculate the GitHub URL extraction accuracy ---
                    total_resumes = len(results)
                    correctly_found = sum(1 for r in results if r.get('parsed_resume_data', {}).get('github_url'))
                    accuracy = (correctly_found / total_resumes) * 100
                    
                    st.markdown(f"### GitHub URL Extraction Accuracy: **{accuracy:.2f}%**")
                    st.info(f"The agent correctly found **{correctly_found}** out of **{total_resumes}** GitHub URLs directly from the resumes.")
                    st.markdown("---")

                    # Display results
                    st.subheader("Screening Results")

                    results.sort(key=lambda x: x.get('final_evaluation', {}).get('score', 0), reverse=True)

                    for result in results:
                        with st.container(border=True):
                            eval_data = result.get('final_evaluation', {})
                            st.markdown(f"### {eval_data.get('candidate_name', 'N/A')}")
                            score = eval_data.get('score', 'N/A')
                            
                            explanation = eval_data.get('explanation', {})
                            
                            if isinstance(score, (int, float)):
                                if score >= 8:
                                    st.progress(score / 10, text=f"**Score:** :green[{score}/10]")
                                elif score >= 5:
                                    st.progress(score / 10, text=f"**Score:** :orange[{score}/10]")
                                else:
                                    st.progress(score / 10, text=f"**Score:** :red[{score}/10]")
                            else:
                                st.markdown(f"**Score:** {score}")
                            
                            if explanation:
                                with st.expander("Show Detailed Explanation"):
                                    st.markdown("#### Strengths")
                                    strengths = explanation.get("strengths", [])
                                    for s in strengths:
                                        st.markdown(f"- {s}")
                                    
                                    st.markdown("#### Weaknesses")
                                    weaknesses = explanation.get("weaknesses", [])
                                    for w in weaknesses:
                                        st.markdown(f"- {w}")
                            else:
                                st.markdown("No detailed explanation available.")

                else:
                    st.error(f"Error from backend: {response.text}")
                    # No status log to empty, so this is now redundant.

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the backend server. Is it running? Error: {e}")
                # No status log to empty, so this is now redundant.


# # streamlit_app.py
# import streamlit as st
# import requests
# import json

# st.set_page_config(page_title="SmartScan AI", page_icon="🔍")

# # Title and description
# st.title("SmartScan AI")
# st.write("An AI-powered tool to screen internship applications based on resumes and GitHub profiles.")

# # File uploader and job description input
# st.markdown("---")
# job_description = st.text_area("Job Description", height=200)
# resume_files = st.file_uploader("Upload Resumes (PDF)", type=["pdf"], accept_multiple_files=True)

# # Define the FastAPI endpoint
# FASTAPI_URL = "http://127.0.0.1:8000/screen"

# if st.button("Screen Candidates"):
#     if not job_description:
#         st.error("Please provide a job description.")
#     elif not resume_files:
#         st.error("Please upload at least one resume.")
#     else:
#         with st.spinner("Screening in progress..."):
#             files = [('resumes', resume) for resume in resume_files]
#             data = {'job_description': job_description}

#             try:
#                 response = requests.post(FASTAPI_URL, files=files, data=data)

#                 if response.status_code == 200:
#                     results = response.json().get("results", [])
#                     st.success("Screening complete!")
#                     st.markdown("---")

#                     # --- FIX: Correctly calculate the GitHub URL extraction accuracy ---
#                     total_resumes = len(results)
#                     correctly_found = sum(1 for r in results if r.get('parsed_resume_data', {}).get('github_url'))
#                     accuracy = (correctly_found / total_resumes) * 100
                    
#                     st.markdown(f"### GitHub URL Extraction Accuracy: **{accuracy:.2f}%**")
#                     st.info(f"The agent correctly found **{correctly_found}** out of **{total_resumes}** GitHub URLs directly from the resumes.")
#                     st.markdown("---")

#                     # Display results
#                     st.subheader("Screening Results")

#                     # Sort results by score
#                     results.sort(key=lambda x: x.get('score', 0), reverse=True)

#                     for result in results:
#                         # Use a container to create a card-like effect
#                         with st.container(border=True):
#                             st.markdown(f"### {result.get('candidate_name', 'N/A')}")
#                             score = result.get('score', 'N/A')
#                             #explanation = result.get('explanation', 'No explanation provided.')

#                             explanation = eval_data.get('explanation', {})
                        
#                             # Use a color-coded progress bar for the score
#                             if isinstance(score, (int, float)):
#                                 if score >= 8:
#                                     st.progress(score / 10, text=f"**Score:** :green[{score}/10]")
#                                 elif score >= 5:
#                                     st.progress(score / 10, text=f"**Score:** :orange[{score}/10]")
#                                 else:
#                                     st.progress(score / 10, text=f"**Score:** :red[{score}/10]")
#                             else:
#                                 st.markdown(f"**Score:** {score}")

#                             # --- FIX: Display strengths and weaknesses inside a dropdown ---
#                             if explanation:
#                                 with st.expander("Show Detailed Explanation"):
#                                     st.markdown("#### Strengths")
#                                     strengths = explanation.get("strengths", [])
#                                     for s in strengths:
#                                         st.markdown(f"- {s}")
                                    
#                                     st.markdown("#### Weaknesses")
#                                     weaknesses = explanation.get("weaknesses", [])
#                                     for w in weaknesses:
#                                         st.markdown(f"- {w}")
#                             else:
#                                 st.markdown("No detailed explanation available.")
#                 else:
#                     st.error(f"Error from backend: {response.text}")

#             except requests.exceptions.RequestException as e:
#                 st.error(f"Could not connect to the backend server. Is it running? Error: {e}")

