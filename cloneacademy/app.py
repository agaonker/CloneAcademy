"""Main Streamlit application for CloneAcademy."""

import os
from pathlib import Path
import json
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
from jinja2 import Environment, FileSystemLoader, select_autoescape
from analyzer import RepositoryAnalyzer

# Load environment variables
env_path = find_dotenv()
if not env_path:
    raise FileNotFoundError("Could not find .env file")

load_dotenv(env_path)

# Get environment variables with defaults
api_key = os.getenv("GOOGLE_API_KEY")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-pro-exp-03-25")
streamlit_port = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
streamlit_address = os.getenv("STREAMLIT_SERVER_ADDRESS", "0.0.0.0")

# Validate required environment variables
if not api_key:
    st.error("GOOGLE_API_KEY not found in environment variables. Please set it in your .env file.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)
model = genai.GenerativeModel(gemini_model)

# Initialize repository analyzer
analyzer = RepositoryAnalyzer()

# Set up Jinja2 environment
template_dir = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

def generate_documentation(repo_info: dict, structure: list, key_files: dict) -> str:
    """Generate documentation using Gemini with a specialized prompt for codebase analysis."""
    # Load and render the template
    template = env.get_template("documentation_prompt.jinja2")
    prompt = template.render(
        repo_info=repo_info,
        structure=structure,
        key_files=key_files,
        model_name=gemini_model,
    )
    
    # Generate the documentation
    response = model.generate_content(prompt)
    return response.text

def main():
    """Run the Streamlit application."""
    st.title("CloneAcademy")
    st.write(
        "Enter a GitHub repository URL to generate documentation about its structure and functionality."
    )

    # Display current model being used
    st.sidebar.info(f"Using Gemini Model: {gemini_model}")

    # Input for GitHub repository URL
    repo_url = st.text_input("GitHub Repository URL")

    if repo_url:
        try:
            with st.spinner("Analyzing repository..."):
                # Fetch repository information
                repo_info = analyzer.fetch_repository(repo_url)
                
                # Analyze repository structure
                structure = analyzer.analyze_structure(repo_url)
                
                # Get key files content
                key_files = analyzer.get_key_files(repo_url)
                
                # Generate documentation
                documentation = generate_documentation(repo_info, structure, key_files)
                
                # Display results
                st.subheader("Repository Information")
                st.json(repo_info)
                
                st.subheader("Repository Structure")
                st.json(structure)
                
                st.subheader("Generated Documentation")
                st.markdown(documentation)
                
                # Save documentation to file
                repo_name = repo_url.split("/")[-1]
                output_dir = Path("output")
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"{repo_name}_documentation.md"
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(documentation)
                st.success(f"Documentation saved to {output_file}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main() 