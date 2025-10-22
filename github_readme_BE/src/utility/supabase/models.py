from pydantic import BaseModel, HttpUrl
from typing import Optional

class Project(BaseModel):
    project_id: Optional[str] = None     
    project_name: str
    git_url: Optional[HttpUrl] = None    
    readme_doc: Optional[str] = None    

class ProjectFile(BaseModel):
    file_id: Optional[str] = None
    project_id: Optional[str] = None
    file_name: str
    file_content: str
    file_summary: str
