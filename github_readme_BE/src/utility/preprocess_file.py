from typing import List, Tuple
from .path import get_agg_file_path, get_readme_output_path

def get_file_data(projectName:str) -> str:    
    """Read the aggregated code file."""
    path = get_agg_file_path(projectName)
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_readme_data(projectName:str) -> str:    
    """Read the generated README file."""
    path = get_readme_output_path(projectName)
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_blocks(projectName: str) -> List[Tuple[str, str]]:
    """
    Parse aggregated file blocks of the form:
        <relative/path>
        <file contents...>
        ---
    Returns list of (path, code) tuples.
    """
    file_data = get_file_data(projectName)
    raw_blocks = [b.strip("\n") for b in file_data.split("\n---\n") if b.strip()]
    blocks: List[Tuple[str, str]] = []
    for b in raw_blocks:
        if "\n" not in b:
            # Block with only a path and no content; skip
            continue
        first_nl = b.find("\n")
        rel_path = b[:first_nl].strip()
        code = b[first_nl + 1 :]
        blocks.append((rel_path, code))
    return blocks