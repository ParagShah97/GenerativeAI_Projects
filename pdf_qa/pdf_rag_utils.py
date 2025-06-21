from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz
import os

from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

def extract_text_from_the_pdf(pdf_path:str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text

def text_splitter(text:str, chunk_size=300, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)

def get_documents(chunks):
    return [Document(chunk) for chunk in chunks]

def embed_and_store(chunks, persist_dir="./pdf_store_dir"):
    add_documents = not os.path.exists(persist_dir)
    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    vector_store = Chroma(
        collection_name="pdf_store",
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )
    if not add_documents:
        documents = get_documents(chunks)
        vector_store.add_documents(documents)
    print("Vector store created successfully!")
    return vector_store

def create_model(model:str = "llama3"):
    model = OllamaLLM(model=model)
    template = """
    You are an exeprt in answering questions from the pdf which already read.
    
    Here are some relevant content: {content}
    
    Here is the question to answer: {question}    
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain

# if __name__ == "__main__":
#     pdf_path = "Parag_Shah_SDE.pdf"
#     text = extract_text_from_the_pdf(pdf_path=pdf_path)
#     chunks = text_splitter(text=text)
#     documents = get_documents(chunks)
#     vector_store = embed_and_store(documents)
#     chain = create_model()
#     retriever = vector_store.as_retriever(
#     search_kwargs={"k": 3}
#     )
    
#     while True:
#         print("\n\n-------------------------------")
#         question = input("Ask your question (q to quit): ")
#         print("\n\n")
#         if question == "q":
#             break
        
#         content = retriever.invoke(question)
#         print("relevant content : ", content, question)
#         result = chain.invoke({"content": content, "question": question})
#         print(result)
    
#     # print(chunks)
    
        
    