# app/services/github_scraper.py
import requests
import os
import base64
import json


def get_github_data(username: str) -> dict:
    """Fetches public user and repository data from the GitHub API."""
    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        return {"error": "GitHub token not set."}
    
    headers = {"Authorization": f"token {github_token}"}
    
    try:
        user_url = f"https://api.github.com/users/{username}"
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        
        print("\n--- GitHub API Rate Limit ---")
        print(f"Limit: {user_response.headers.get('X-RateLimit-Limit')}")
        print(f"Remaining: {user_response.headers.get('X-RateLimit-Remaining')}")
        print(f"Reset: {user_response.headers.get('X-RateLimit-Reset')}")
        print("-----------------------------\n")
        
        user_data = user_response.json()
        
        repos_url = f"https://api.github.com/users/{username}/repos"
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()
        
        projects = []
        if isinstance(repos_data, list):
            # --- NEW: Iterate and get more detailed info for each repo ---
            for repo in repos_data:
                repo_name = repo.get("name")
                project_info = {
                    "name": repo_name,
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "readme_content": None,
                    "recent_commits": []
                }
                
                # Fetch README.md content
                readme_url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
                readme_response = requests.get(readme_url, headers=headers)
                if readme_response.status_code == 200:
                    readme_data = readme_response.json()
                    # The content is Base64 encoded, so we need to decode it
                    readme_content = base64.b64decode(readme_data.get("content")).decode('utf-8')
                    project_info["readme_content"] = readme_content

                # Fetch recent commits
                commits_url = f"https://api.github.com/repos/{username}/{repo_name}/commits"
                commits_response = requests.get(commits_url, headers=headers)
                if commits_response.status_code == 200:
                    commits_data = commits_response.json()
                    for commit in commits_data[:3]: # Get the last 3 commits
                        project_info["recent_commits"].append({
                            "message": commit.get("commit").get("message"),
                            "sha": commit.get("sha")[:7]
                        })
                
                projects.append(project_info)
        
        return {
            "username": user_data.get("login"),
            "public_repos": user_data.get("public_repos"),
            "projects": projects,
            "followers": user_data.get("followers")
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

def find_github_profile_by_name(name: str) -> str | None:
    """Finds a GitHub profile URL based on a name (fallback)."""
    search_query = name.replace(" ", "+")
    search_url = f"https://api.github.com/search/users?q={search_query}"
    
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        search_results = response.json()
        if search_results["items"]:
            return search_results["items"][0]["html_url"]
    except requests.exceptions.RequestException as e:
        print(f"Error during GitHub profile search: {e}")
    return None




# # app/services/github_scraper.py
# import requests
# import os


# def get_github_data(username: str) -> dict:
#     """Fetches public user and repository data from the GitHub API."""
#     github_token = os.getenv("GITHUB_TOKEN")
#     if not github_token:
#         return {"error": "GitHub token not set."}
    
#     headers = {"Authorization": f"token {github_token}"}
    
#     try:
#         user_url = f"https://api.github.com/users/{username}"
#         user_response = requests.get(user_url, headers=headers)
#         user_response.raise_for_status()
        
#         # --- NEW: Print rate limit information ---
#         print("\n--- GitHub API Rate Limit ---")
#         print(f"Limit: {user_response.headers.get('X-RateLimit-Limit')}")
#         print(f"Remaining: {user_response.headers.get('X-RateLimit-Remaining')}")
#         print(f"Reset: {user_response.headers.get('X-RateLimit-Reset')}")
#         print("-----------------------------\n")
        
#         user_data = user_response.json()
        
#         repos_url = f"https://api.github.com/users/{username}/repos"
#         repos_response = requests.get(repos_url, headers=headers)
#         repos_response.raise_for_status()
#         repos_data = repos_response.json()
        
#         projects = []
#         if isinstance(repos_data, list):
#             for repo in repos_data:
#                 projects.append({
#                     "name": repo.get("name"),
#                     "description": repo.get("description"),
#                     "language": repo.get("language"),
#                     "stars": repo.get("stargazers_count")
#                 })
        
#         return {
#             "username": user_data.get("login"),
#             "public_repos": user_data.get("public_repos"),
#             "projects": projects
#         }
#     except requests.exceptions.RequestException as e:
#         return {"error": f"API request failed: {e}"}
    
# # def get_github_data(username: str) -> dict:
# #     """Fetches public user and repository data from the GitHub API."""
# #     github_token = os.getenv("GITHUB_TOKEN")
# #     if not github_token:
# #         return {"error": "GitHub token not set."}

# #     headers = {"Authorization": f"token {github_token}"}

# #     try:
# #         user_url = f"https://api.github.com/users/{username}"
# #         user_response = requests.get(user_url, headers=headers)
# #         user_response.raise_for_status()
# #         user_data = user_response.json()

# #         repos_url = f"https://api.github.com/users/{username}/repos"
# #         repos_response = requests.get(repos_url, headers=headers)
# #         repos_response.raise_for_status()
# #         repos_data = repos_response.json()

# #         projects = []
# #         if isinstance(repos_data, list):
# #             for repo in repos_data:
# #                 projects.append({
# #                     "name": repo.get("name"),
# #                     "description": repo.get("description"),
# #                     "language": repo.get("language"),
# #                     "stars": repo.get("stargazers_count")
# #                 })

# #         return {
# #             "username": user_data.get("login"),
# #             "public_repos": user_data.get("public_repos"),
# #             "projects": projects
# #         }
# #     except requests.exceptions.RequestException as e:
# #         return {"error": f"API request failed: {e}"}

# def find_github_profile_by_name(name: str) -> str | None:
#     """Finds a GitHub profile URL based on a name (fallback)."""
#     search_query = name.replace(" ", "+")
#     search_url = f"https://api.github.com/search/users?q={search_query}"

#     try:
#         response = requests.get(search_url)
#         response.raise_for_status()
#         search_results = response.json()
#         if search_results["items"]:
#             return search_results["items"][0]["html_url"]
#     except requests.exceptions.RequestException as e:
#         print(f"Error during GitHub profile search: {e}")
#     return None 

