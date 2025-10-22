from typing import Optional
from pathlib import Path

PROJECT_MARKERS = ("pyproject.toml", "setup.cfg", "setup.py", ".git", ".env")

def get_project_root(start: Optional[Path] = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here] + list(here.parents):
        if any((parent / m).exists() for m in PROJECT_MARKERS):
            return parent
    return here.parent

def get_agg_file_path(projectName: str):
    project_root = get_project_root()    
    out_dir  = (project_root / "src" / "output" / "aggregate" / projectName).resolve()
    out_path = out_dir / "aggregated_code.txt"
    return out_path

def get_git_repo_path(projectName:str):
    project_root = get_project_root()
    repo_dir = (project_root / "src" / "output" / "git" / projectName).resolve()
    return repo_dir

def get_readme_output_path(projectName: str):
    project_root = get_project_root()    
    out_dir  = (project_root / "src" / "output" / "readme" / projectName).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "readme.md"
    return out_path
    