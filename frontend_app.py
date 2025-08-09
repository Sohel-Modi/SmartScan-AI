# streamlit_app.py
import streamlit as st
import requests
import json

st.set_page_config(page_title="SmartScan AI", page_icon="🔍")

# Title and description
st.title("SmartScan AI")
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
        with st.spinner("Screening in progress..."):
            files = [('resumes', resume) for resume in resume_files]
            data = {'job_description': job_description}

            try:
                response = requests.post(FASTAPI_URL, files=files, data=data)

                if response.status_code == 200:
                    results = response.json().get("results", [])
                    st.success("Screening complete!")
                    st.markdown("---")

                    # Display results
                    st.subheader("Screening Results")

                    # Sort results by score
                    results.sort(key=lambda x: x.get('score', 0), reverse=True)

                    for result in results:
                        st.card(f"### {result.get('candidate_name', 'N/A')}")
                        score = result.get('score', 'N/A')
                        explanation = result.get('explanation', 'No explanation provided.')

                        # Use a color-coded score bar
                        if isinstance(score, (int, float)):
                            if score >= 8:
                                color = "green"
                            elif score >= 5:
                                color = "orange"
                            else:
                                color = "red"

                            st.progress(score / 10, text=f"**Score:** {score}/10")
                        else:
                            st.markdown(f"**Score:** {score}")

                        with st.expander("Show Explanation"):
                            st.write(explanation)
                else:
                    st.error(f"Error from backend: {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the backend server. Is it running? Error: {e}")