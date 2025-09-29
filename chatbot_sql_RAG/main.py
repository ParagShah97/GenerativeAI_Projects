from loadCSV import LoadCSV
from querySQLDBwithLLM import QueryDB

from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
# To create a prompt template.
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from dotenv import load_dotenv
import os
import re

load_dotenv()



def extract_sql(s: str) -> str:
    s = re.sub(r"^\s*SQLQuery:\s*", "", s, flags=re.I)
    s = re.sub(r"^```(?:sql)?\s*", "", s.strip(), flags=re.I)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()

def loadCSV():
    path = os.getenv("PATH_TO_CSV")
    headers = ["Patient_ID", "Age", "Gender", "Diagnosis", "Admitted"]
    inst = LoadCSV(path, headers)
    inst.loadToSQLDB()
    
def getLLM():
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key,
    temperature=0.2,
    streaming=True,
    )
    return llm

def callLLMForQueryResults():
    DB = QueryDB().getDBConnection()   # SQLDatabase instance
    LLM = getLLM()

    get_sql_query = create_sql_query_chain(LLM, DB)   # question -> raw SQL text
    clean_sql = RunnableLambda(extract_sql)           # raw -> clean SQL string
    execute_query = QuerySQLDatabaseTool(db=DB)       # expects {"query": "<SQL>"}

    prompt_for_output_ans = PromptTemplate.from_template(
        "Given the user question, corresponding SQL, and SQL result, answer the question.\n\n"
        "Question: {question}\nSQL Query: {query}\nSQL Result: {result}\nAnswer:"
    )
    final_ans_chain = prompt_for_output_ans | LLM | StrOutputParser()

    # Stage 1: compute SQL once and store under "sql"
    # Stage 2: execute using {"query": itemgetter('sql')}
    # Stage 3: expose "query" for the final prompt
    final = (
        RunnablePassthrough
            .assign(sql = get_sql_query | clean_sql)
            .assign(result = {"query": itemgetter("sql")} | execute_query)
            .assign(query = itemgetter("sql"))
        | final_ans_chain
    )

    print(final.invoke({"question": "How many male have FLU ?"}))
    
    

def main():
    # loadCSV()
    # Get the instance of DB here.
    callLLMForQueryResults()
    # sql = extract_sql(response)
    # print(response)
    # print(sql)
    # print(DB.run(sql))
    
    pass
    
    
    


if __name__ == "__main__":
    main()
