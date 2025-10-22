# 🧠 Chatbot SQL RAG

This project demonstrates how to build a **retrieval-augmented generation (RAG) chatbot** that works with a MySQL database.  
It covers:

- Loading **CSV data** into a MySQL database with SQLAlchemy.
- Defining ORM models (`PatientsData`) and managing connections.
- Integrating with **LangChain’s SQLDatabase** utility.
- Using **LLMs to generate SQL queries** from natural language.
- Executing those queries safely and returning **human-readable answers**.

---

## 📂 Project Structure

```
chatbot_sql_RAG/
│── database.py         # SQLAlchemy engine, session, Base, get_db
│── model.py            # ORM model (PatientsData)
│── loadCSV.py          # Generic CSV loader -> SQLAlchemy models
│── querySQLDBwithLLM.py# Wrapper for SQLDatabase
│── main.py             # Entrypoint: LLM pipeline execution
│── requirements.txt    # Dependencies
│── .env                # DB URI + API keys
```

---

## ⚙️ Setup

1. **Clone repo & create venv**
   ```bash
   git clone https://github.com/yourname/chatbot_sql_RAG.git
   cd chatbot_sql_RAG
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows
   ```

2. **Install deps**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables** in `.env`:
   ```ini
   MYSQL_URI=mysql+pymysql://root:root@localhost:3306/sql_chatbot
   OPENAI_API_KEY=sk-xxxx
   PATH_TO_CSV=./patients.csv
   ```

4. **Prepare database**
   ```sql
   CREATE DATABASE sql_chatbot;
   ```

---

## 🗄️ Database Schema

Example model in `model.py`:

```python
class Patients(Base):
    __tablename__ = "PatientsData"

    Patient_ID = Column(Integer, primary_key=True)
    Age        = Column(Integer)
    Gender     = Column(String(50))
    Diagnosis  = Column(String(200))
    Admitted   = Column(String(200))
```

---

## 📥 Load CSV into MySQL

Generic CSV loader (`loadCSV.py`) reads headers from CSV and maps to ORM models:

```python
loader = LoadCSV("patients.csv")
rows = loader.loadToSQLDB(Patients)
print(f"Inserted {rows} rows")
```

Supports:
- Handling missing values
- Type coercion (`Int64`, `Float`, `DateTime`, etc.)
- Bulk insert for performance

---

## 🔗 LangChain Integration

We use `SQLDatabase` from `langchain_community`:

```python
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(DATABASE_URL, include_tables=["PatientsData"])
```

This object lets LangChain inspect schema and generate queries.

---

## 🤖 Natural Language → SQL → Answer

### SQL Generation
```python
from langchain.chains.sql_database.query import create_sql_query_chain

sql_chain = create_sql_query_chain(llm, db)
```

### SQL Execution
```python
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool

execute_query = QuerySQLDatabaseTool(db=db)
```

### Cleaning Queries
Sometimes LLM adds prefixes like `SQLQuery:` or code fences. We strip them:

```python
import re
def extract_sql(s: str) -> str:
    s = re.sub(r"^\s*SQLQuery:\s*", "", s, flags=re.I)
    s = re.sub(r"^```(?:sql)?\s*", "", s.strip(), flags=re.I)
    s = re.sub(r"\s*```$", "", s)
    return s.strip()
```

### Final Pipeline (LCEL style)
```python
from operator import itemgetter
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

clean_sql = RunnableLambda(extract_sql)

prompt = PromptTemplate.from_template(
    "Given the user question, SQL query, and SQL result, answer:\n\n"
    "Question: {question}\nSQL Query: {query}\nSQL Result: {result}\nAnswer:"
)

final_chain = (
    RunnablePassthrough
      .assign(sql = sql_chain | clean_sql)
      .assign(result = {"query": itemgetter("sql")} | execute_query)
      .assign(query = itemgetter("sql"))
    | prompt
    | llm
    | StrOutputParser()
)

print(final_chain.invoke({"question": "How many male patients have Flu?"}))
```

---

## 🚀 Example Run

```
> How many male patients have Flu?
SQL Query: SELECT COUNT(*) FROM PatientsData WHERE Gender='Male' AND Diagnosis='Flu';
SQL Result: [(42,)]
Answer: There are 42 male patients diagnosed with Flu.
```

---

## ⚠️ Notes & Gotchas
- **Safe mode in MySQL Workbench** may block deletes/updates without key filters → disable safe mode or always include PKs.
- **Case sensitivity:** Use `include_tables=["PatientsData"]` to ensure the LLM uses correct casing.
- **Deprecated imports:** Use `QuerySQLDatabaseTool` from `langchain_community`, not `QuerySQLDataBaseTool`.
