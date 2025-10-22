from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .models.request import RepoRequest
from .utility.git import clone_repo
from .utility.file_crawler import aggregate_code
from .utility.preprocess_file import parse_blocks, get_readme_data
from .utility.llm_util import generate_readme_file
from .utility.supabase.models import Project
from .utility.supabase.database import save_projects, save_readme, get_projects_list, get_project_files, get_readme

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for now keeping *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return "The App is up and running"

@app.post("/repo")
async def cloneAndGenerate(body: RepoRequest):
    print("body ", body)
    
    project = Project(project_name=body.project_name, git_url=body.git_url)
    # Save the project info to the database.
    save_projects(project)
    # Clone the repository
    clone_repo(body.git_url, body.project_name)
    # Preprocess and aggregate code files
    aggregate_code(body.project_name)    
    ret = generate_readme_file(projectName=body.project_name) 
    return {'message': "Success", 'isSuccess': True, 'statusCode': 201}

@app.get("/projects")
async def get_all_projects():
    print("Fetching all projects")
    returnlst = get_projects_list()
    return returnlst

@app.get("/projects/{project_id}/files")
async def get_file_data(project_id: str):
    print("Fetching files for project_id: ", project_id)
    files = get_project_files(project_id)
    return files


@app.get("/projects/{project_id}/readme")
async def get_readme_content(project_id: str) -> str:
    return get_readme(project_id)
    