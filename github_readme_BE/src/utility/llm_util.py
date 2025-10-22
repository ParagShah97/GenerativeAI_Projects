import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Tuple
from .supabase.models import ProjectFile, Project
from .supabase.database import save_files_data, save_readme

from .config import MAX_CHARS_PER_FILE_SNIPPET, MAX_FILES_TO_SUMMARIZE
from .preprocess_file import parse_blocks
from .path import get_readme_output_path

load_dotenv()

def getOpenAIKey():
    key = os.getenv("OPENAI_API_KEY")
    return key
    

def get_llm_model() -> ChatOpenAI:
    """Configured LLM client."""
    key = getOpenAIKey()
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=key,
        temperature=0.3,
        streaming=False,
    )

def summarize_files(LLM: ChatOpenAI, blocks: List[Tuple[str, str]], projectName: str) -> str:
    """
    Map step: summarize each file briefly to keep context tiny.
    Returns a concatenated multi-file summary string.
    """
    file_level_data = []
    prompt = PromptTemplate.from_template(
        "You are a precise code summarizer. Summarize the file below for a README.\n"
        "Focus on: purpose, key responsibilities, important functions/classes/exports, routes/CLI, "
        "external deps, and how it fits the project. No code snippets.\n\n"
        "PATH: {path}\n"
        "CONTENT:\n```\n{code}\n```\n\n"
        "Output 3–6 concise bullet points."
    )
    chain = prompt | LLM | StrOutputParser()

    summaries: List[str] = []
    limit = min(MAX_FILES_TO_SUMMARIZE, len(blocks))
    for i in range(limit):
        path, code = blocks[i]
        snippet = code[:MAX_CHARS_PER_FILE_SNIPPET]
        # print("Summarizing file:", path, len(code))
        try:
            s = chain.invoke({"path": path, "code": snippet})
            summaries.append(f"### {path}\n{s.strip()}\n")
            project_file = ProjectFile(
                file_name=path,
                file_content=code,
                file_summary=s.strip()
            )
            # print("Adding file summary to database: ", project_file)
            file_level_data.append(project_file)
        except Exception as e:
            # Skip problematic files but continue
            
            print(f"Error summarizing file {path}: {e}")
            summaries.append(f"### {path}\n- (summary failed: {e})\n")
    # print("Saving file-level summaries to database...", file_level_data)
    save_files_data(projectName, file_level_data)
    return "\n".join(summaries)

def compose_readme(LLM: ChatOpenAI, multi_file_summary: str) -> str:
    """
    Reduce + final step: produce a complete README.md
    from the compact multi-file summary.
    """
    final_prompt = PromptTemplate.from_template(
        "You will write a high-quality README.md for a repository using the condensed file summaries below.\n"
        "Write concise, actionable documentation without large code blocks. Use fenced blocks only for commands.\n\n"
        "FILE SUMMARIES:\n{summaries}\n\n"
        "Produce README with these sections (only include a section if relevant):\n"
        "1. Overview (what it is and why it exists)\n"
        "2. Tech Stack\n"
        "3. Project Structure (high-level; list major dirs/files and roles)\n"
        "4. Key Components/Modules (what they do)\n"
        "5. Setup (install) [include information to create virtual env or other way to install the dependency if needed.]\n"
        "6. Usage (run, CLI or API quickstart; sample commands/endpoints)\n"
        "7. Configuration (env vars table: NAME | Purpose | Required | Default)\n"
        "8. Data Model (entities/relations if present)\n"
        "9. Testing (how to run tests)\n"
        "10. Deployment (Docker/CI/CD/cloud hints)\n"
        "11. Roadmap/Limitations\n"
        "Keep it crisp and dev-friendly."
    )
    chain = final_prompt | LLM | StrOutputParser()
    return chain.invoke({"summaries": multi_file_summary})

def generate_readme_file(projectName: str) -> str:
    """
    Orchestrates the map → reduce → write pipeline.
    Returns the output README path.
    """
    LLM = get_llm_model()
    blocks = parse_blocks(projectName)
    README_OUTPUT_PATH = get_readme_output_path(projectName)

    # Map: per-file micro-summaries (bounded by limits above)
    multi_file_summary = summarize_files(LLM, blocks, projectName)

    # Reduce/final: compose full README from condensed context
    readme_text = compose_readme(LLM, multi_file_summary)
    
    # Save README to database
    project = Project(project_name=projectName, readme_doc=readme_text)
    # print("Saving README to database for project:", projectName)
    save_readme(project)

    # Write output README

    with open(README_OUTPUT_PATH, "w", encoding="utf-8") as outf:
        outf.write(readme_text)

    return README_OUTPUT_PATH