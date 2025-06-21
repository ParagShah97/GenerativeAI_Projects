from langchain_ollama import OllamaEmbeddings

embeddings = OllamaEmbeddings(model="nomic-embed-text")
# embedding = embeddings.embed_query("Sample test review about pizza.")
# print("✅ Sample embedding length:", len(embedding))

from langchain_chroma import Chroma

vector_store = Chroma(
    collection_name="foo",
    embedding_function=embeddings
)

from langchain_core.documents import Document

document_1 = Document(page_content="foo", metadata={"baz": "bar"})
document_2 = Document(page_content="thud", metadata={"bar": "baz"})
document_3 = Document(page_content="i will be deleted :(")

documents = [document_1, document_2, document_3]
ids = ["1", "2", "3"]
vector_store.add_documents(documents=documents, ids=ids)
print("✅ Documents added to vector store.")