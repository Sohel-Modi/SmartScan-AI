# SmartScan AI
**SmartScan** is a modern, AI-powered application designed to automate and enhance the initial screening process for internship and entry-level positions. Unlike traditional keyword-based Applicant Tracking Systems (ATS), this tool performs a holistic evaluation of candidates by synthesizing data from their resumes and their GitHub profiles. The core innovation is its ability to provide an explainable score, giving recruiters clear, contextual reasoning for each candidate's ranking.

-------------------------

**Key Features**

- **Holistic Evaluation:** The system combines data from two crucial sources: a candidate's resume and their public GitHub profile.

- **Intelligent Data Extraction:** An LLM-powered agent intelligently parses  unstructured resume text into a clean, structured JSON format.

- **Smart Fallback Mechanism:** If a GitHub URL is not found on a resume, the system automatically attempts to find the candidate's profile based on their name, ensuring a complete evaluation.

- **Explainable AI Scoring:** The core of the project. A dedicated agent provides a contextual score (1-10) with a detailed, human-readable explanation, highlighting a candidate's strengths and weaknesses with specific examples from their projects and contributions.

- **Rapid & Scalable Backend:** Built with FastAPI, the backend can handle multiple screening requests concurrently, making it fast and efficient.

- **User-Friendly Frontend:** A simple, powerful Streamlit interface allows anyone to upload resumes and get results instantly.

-----------------

**AI Agents**

**Resume Parser Agent :**  Uses an LLM to extract structured data from resumes.

**Evaluator Agent :**  The core intelligence that synthesizes all data to provide a score and a structured explanation.


----------------------


**Technologies Used**

**Backend :** FastAPI

**Frontend :** Streamlit

**AI/ML :** LangChain, OpenAI API

**Utilities :** pypdf, requests, python-dotenv

**Version Control :** Git


-------------------

**How to Run Locally**

Follow these steps to set up and run the application on your local machine.

1. **Prerequisites**
        
        Python 3.8+ installed.

        Git installed.

2. An OpenAI API Key and a GitHub Personal Access Token (PAT) with public repository read access.

3. **Setup**

    Clone the repository and set up the environment:

        git clone https://github.com/your-username/SmartScan.git
        cd SmartScan
        python -m venv screener_env
        screener_env\Scripts\activate  # Use `source screener_env/bin/activate` on macOS/Linux


4. **Install dependencies:**

        pip install -r requirements.txt


5. **Configure API keys:**

    Create a file named .env in the root of the project and add your API keys.

        OPENAI_API_KEY="your_openai_api_key_here"
        GITHUB_TOKEN="your_github_personal_access_token_here"


6. **Run the backend server:**
    
    Open your terminal in the project directory and run the FastAPI server.

        uvicorn app.main:app --reload


7. **Run the frontend app:**

    Open a second terminal window, navigate to the project directory, and run the Streamlit app.

        streamlit run streamlit_app.py

------------------


**Future Enhancements**

- **LinkedIn Integration :**  Scrape public LinkedIn profiles for a more comprehensive professional overview.

- **Advanced Data Sources :** Add support for platforms like LeetCode or HackerRank to evaluate coding skills directly.

- **Feedback Loop :** Implement a system where recruiters can provide feedback on the AI's evaluation, which can be used to fine-tune the model for better accuracy.

- **Caching :** Implement caching for GitHub API requests to improve performance and avoid hitting rate limits. 
