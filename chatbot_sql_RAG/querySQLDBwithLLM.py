from langchain_community.utilities import SQLDatabase
from database import DATABASE_URL

class QueryDB:
    def __init__(self):
        self.db = SQLDatabase.from_uri(DATABASE_URL)
    
    def getDBConnection(self):
        return self.db
 