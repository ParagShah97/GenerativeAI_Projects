import os
from pathlib import Path
from typing import Optional, Set

from .config import CODE_EXTS, DEFAULT_EXCLUDE_DIRS

PROJECT_MARKERS = ("pyproject.toml", "setup.cfg", "setup.py", ".git", ".env")

def get_project_root(start: Optional[Path] = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in [here] + list(here.parents):
        if any((parent / m).exists() for m in PROJECT_MARKERS):
            return parent
    return here.parent

def _sanitize_project_name(name: str) -> str:
    # Remove quotes/whitespace and collapse any path components to just the last segment
    # (prevents users from passing 'output/git/foo' or 'foo/' etc.)
    clean = Path(str(name).strip().strip('"\''))  # strip whitespace and quotes
    return clean.name  # last path segment only

def aggregate_code(
    project_name: str,
    include_exts: Optional[Set[str]] = None,
    exclude_dirs: Optional[Set[str]] = None,
    max_bytes_per_file: Optional[int] = None,
) -> int:
    """
    Read from <root>/output/git/<project_name> and write to
    <root>/output/aggregate/<project_name>/aggregated_code.txt
    """
    project_root = get_project_root()
    pname = _sanitize_project_name(project_name)

    repo_dir = (project_root / "src" / "output" / "git" / pname).resolve()
    out_dir  = (project_root / "src" / "output" / "aggregate" / pname).resolve()
    out_path = out_dir / "aggregated_code.txt"

    # --- helpful debug when things go wrong ---
    # print(f"[aggregate_code] project_root={project_root}")
    # print(f"[aggregate_code] project_name(raw)={repr(project_name)}  sanitized={pname}")
    # print(f"[aggregate_code] repo_dir={repo_dir}  exists={repo_dir.exists()}")

    if not repo_dir.exists():
        raise FileNotFoundError(
            f"Repo directory not found: {repo_dir}\n"
            f"Expected structure: output/git/{pname}/\n"
            f"(Got project_name={repr(project_name)} → sanitized={pname})"
        )

    out_dir.mkdir(parents=True, exist_ok=True)

    include_exts = include_exts or CODE_EXTS
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_dirs_lower = {d.lower() for d in exclude_dirs}

    files_written = 0
    candidate_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(repo_dir):
        dirnames[:] = [d for d in dirnames if d.lower() not in exclude_dirs_lower]
        for fname in filenames:
            if Path(fname).suffix.lower() in include_exts:
                candidate_files.append(Path(dirpath) / fname)

    candidate_files.sort(key=lambda p: str(p.relative_to(repo_dir)).lower())

    with out_path.open("w", encoding="utf-8", errors="ignore") as out:
        for fpath in candidate_files:
            try:
                if max_bytes_per_file is not None and fpath.stat().st_size > max_bytes_per_file:
                    continue
                rel = fpath.relative_to(repo_dir).as_posix()
                content = fpath.read_text(encoding="utf-8", errors="ignore")

                out.write(f"Path - {rel}\n\n")
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")
                out.write("---\n")
                files_written += 1
            except Exception:
                continue

    return files_written