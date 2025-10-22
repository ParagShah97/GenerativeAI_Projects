from pydantic import BaseModel

class RepoRequest(BaseModel):
    project_name:str
    git_url:str
