import os
from dotenv import load_dotenv
from supabase import create_client, Client
from ..config import PROJECT_TABLE, PROJECT_FILES_TABLE
from .models import Project, ProjectFile
from typing import List
import uuid
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_projects(requestJson: Project):
    data = {
        "project_name": requestJson.project_name,
        "git_url": str(requestJson.git_url),
        "readme_doc": ""
    }
    print("Saving project data: ", data)
    supabase.table(PROJECT_TABLE).insert(data).execute()

def save_readme(requestJson: Project):
    data = {
        "readme_doc": requestJson.readme_doc
    }
    supabase.table(PROJECT_TABLE).update(data).eq("project_name", requestJson.project_name).execute()
    

def save_files_data(projectName: str, requestJson: List[ProjectFile]):
    # Get the project ID based on project name
    response = supabase.table(PROJECT_TABLE).select("project_id").eq("project_name", projectName).execute()
    project_data = response.data
    print("Project data fetched for file saving: ", project_data)
    # collect records and insert them into the PROJECT_FILES_TABLE
    records = []
    for pf in requestJson:
        records.append({
            "project_id": project_data[0]["project_id"],
            "file_name": pf.file_name,
            "file_content": pf.file_content,
            "file_summary": pf.file_summary
        })
    print("Saving file data: ", records)
    if records:
        supabase.table(PROJECT_FILES_TABLE).insert(records).execute()
        
def get_projects_list():
    response = supabase.table(PROJECT_TABLE).select("project_id, project_name").execute()
    project_data = response.data
    returnLst = []
    for pd in project_data:
        returnLst.append({
            "project_id": pd["project_id"],
            "project_name": pd["project_name"]
        })
    return returnLst

def get_project_files(project_id: str) -> List[ProjectFile]:
    response = supabase.table(PROJECT_FILES_TABLE).select("*").eq("project_id", project_id).execute()
    file_data = response.data
    project_files = []
    for fd in file_data:
        project_file = ProjectFile(
            file_id=fd["file_id"],
            project_id=fd["project_id"],
            file_name=fd["file_name"],
            file_content=fd["file_content"],
            file_summary=fd["file_summary"]
        )
        project_files.append(project_file)
    return project_files

def get_readme(project_id: str) -> str:
    response = supabase.table(PROJECT_TABLE).select("readme_doc").eq("project_id", project_id).execute()
    project_data = response.data
    if project_data and "readme_doc" in project_data[0]:
        return project_data[0]["readme_doc"]
    return ""