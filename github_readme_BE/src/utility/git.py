from pathlib import Path
from git import Repo

def clone_repo(repo_url: str, project_name: str):
    base_dir = Path(__file__).resolve().parent.parent  # go up to project root
    clone_dir = base_dir / "output" / "git" / project_name
    
    print("Base dir : ", base_dir)
    print("Clone dir : ", clone_dir)

    try:
        Repo.clone_from(repo_url, str(clone_dir))
        print(f"Repository cloned into {clone_dir}")
    except Exception as e:
        print("Error cloning repository:", e)
