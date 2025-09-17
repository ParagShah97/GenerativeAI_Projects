from pydantic import BaseModel

class CompleteRequest(BaseModel):
    query:str