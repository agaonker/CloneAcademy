"""Repository analysis module for CloneAcademy."""

from typing import List, Dict, Optional
import os
from dotenv import load_dotenv, find_dotenv
import requests
import base64
import time

# Load environment variables
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)

class RepositoryAnalyzer:
    """Analyzes GitHub repositories and generates documentation."""

    def __init__(self):
        """Initialize the analyzer."""
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds

    def _rate_limit(self):
        """Ensure we don't exceed GitHub's rate limits."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def fetch_repository(self, repo_url: str) -> Dict:
        """Fetch repository information from GitHub."""
        try:
            # Extract owner and repo name from URL
            parts = repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            
            # Use public GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            self._rate_limit()
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "name": repo_data.get("name", repo),
                    "description": repo_data.get("description", ""),
                    "url": repo_data.get("html_url", repo_url),
                    "stars": repo_data.get("stargazers_count", 0),
                    "forks": repo_data.get("forks_count", 0),
                }
            else:
                # Fallback to basic information if API fails
                return {
                    "name": repo,
                    "url": repo_url,
                }
        except Exception as e:
            raise Exception(f"Failed to fetch repository: {e}")

    def get_file_content(self, repo_url: str, path: str) -> Optional[str]:
        """Get the content of a specific file from the repository."""
        try:
            parts = repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            
            # Try raw GitHub content first (no rate limits)
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
            self._rate_limit()
            response = requests.get(raw_url)
            
            if response.status_code == 200:
                return response.text
            
            # If raw content fails, try the API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            self._rate_limit()
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                content_data = response.json()
                if "content" in content_data:
                    return base64.b64decode(content_data["content"]).decode('utf-8')
            
            return None
        except Exception as e:
            raise Exception(f"Failed to fetch file content: {e}")

    def analyze_structure(self, repo_url: str) -> List[Dict]:
        """Analyze the repository structure using GitHub API."""
        try:
            parts = repo_url.strip("/").split("/")
            owner, repo = parts[-2], parts[-1]
            
            # Use public GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            self._rate_limit()
            response = requests.get(api_url, headers=self.headers)
            
            if response.status_code == 200:
                contents = response.json()
                structure = []
                
                for item in contents:
                    if item["type"] == "file" and item["name"].endswith(('.py', '.md', '.txt', '.yaml', '.yml')):
                        structure.append({
                            "path": item["path"],
                            "type": "file",
                            "size": item["size"],
                        })
                
                return structure
            else:
                raise Exception(f"Failed to fetch repository contents: {response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to analyze repository structure: {e}")

    def get_key_files(self, repo_url: str) -> Dict[str, str]:
        """Get the content of key files (README.md, requirements.txt, etc.)."""
        key_files = {
            "README.md": None,
            "requirements.txt": None,
            "pyproject.toml": None,
            "setup.py": None,
        }
        
        for file_name in key_files:
            content = self.get_file_content(repo_url, file_name)
            if content:
                key_files[file_name] = content
                
        return key_files 