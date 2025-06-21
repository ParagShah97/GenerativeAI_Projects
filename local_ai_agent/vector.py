from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

df = pd.read_csv("realistic_restaurant_reviews.csv")
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chroma_langchain_db"
# Here we check if the database already exists
# If it does not exist, we will add documents to it
add_documents = not os.path.exists(db_location)

# Here we create the database if it does not exist
if add_documents:
    documents = []
    ids = []
    
    # Iterate through the DataFrame and create Document objects
    # Each document will contain the title and review text, along with metadata
    for i, row in df.iterrows():
        # Create a Document object for each review
        # The page_content will be a combination of the title and review text
        # Metadata is for storing additional information like rating and date
        # The id is set to the index of the row
        document = Document(   
            page_content=row["Title"] + " " + row["Review"],
            metadata={
                "rating": row["Rating"],
                "date": row["Date"],
            },
            id=str(i)
        )
        # Append the document and its id to the lists
        ids.append(str(i))
        documents.append(document)

# Create a Chroma vector store to store the documents
# The collection name is set to "restaurant_reviews"
# The persist_directory is where the database will be stored
# The embedding_function is set to the Ollama embeddings model
vector_store = Chroma(
    collection_name="restaurant_reviews",
    persist_directory=db_location,
    embedding_function=embeddings,
)

# If the database does not exist, we add the documents to the vector store
# The ids are used to uniquely identify each document in the vector store
if add_documents:
    vector_store.add_documents(documents, ids=ids)


print("Vector store created and documents added successfully.")

# Create a retriever from the vector store
# The retriever will be used to search for relevant documents based on a query
# The search_kwargs specify the number of results to return (k=2 in this case)
retriever = vector_store.as_retriever(
    search_kwargs={"k": 2}
)