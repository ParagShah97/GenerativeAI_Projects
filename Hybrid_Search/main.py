import os
import time
from dotenv import load_dotenv

# Pinecone (new SDK)
from pinecone import Pinecone, ServerlessSpec

# LangChain pieces
from langchain_huggingface import HuggingFaceEmbeddings


#  Class PineconeHybridSearchRetriever is responsible for searching both symentic and semantic search.
from langchain_community.retrievers import PineconeHybridSearchRetriever

# Sparse encoder (BM25/TF-IDF)
from pinecone_text.sparse import BM25Encoder


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def wait_for_index_ready(pc: Pinecone, index_name: str, timeout_s: int = 120) -> None:
    """Poll until index 'ready' or timeout."""
    start = time.time()
    while True:
        desc = pc.describe_index(index_name)
        ready = desc.get("status", {}).get("ready", False)
        if ready:
            return
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Index {index_name} not ready after {timeout_s}s")
        time.sleep(2)


def main():
    load_dotenv()

    # --- 1) Keys / config ---
    # Make sure you set these in a .env file:
    # PINECONE_API_KEY=...
    # HF_TOKEN=...
    PINECONE_API_KEY = require_env("PINECONE_API_KEY")
    HF_TOKEN = require_env("HF_TOKEN")

    # Index config
    INDEX_NAME = "hybrid-search-langchain-pinecone"  
    DIMENSION = 384  # matches 'all-MiniLM-L6-v2'
    METRIC = "dotproduct"  # good for dense+sparse hybrid scoring
    CLOUD = "aws"
    REGION = "us-east-1"

    # --- 2) Init Pinecone ---
    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Create index if it doesn't exist
    existing = {idx["name"] for idx in pc.list_indexes()}
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=DIMENSION,
            metric=METRIC,
            spec=ServerlessSpec(cloud=CLOUD, region=REGION),
        )
        print(f"Creating index '{INDEX_NAME}'...")
        wait_for_index_ready(pc, INDEX_NAME)
        print("Index is ready")
    else:
        print(f"Index '{INDEX_NAME}' already exists")

    # Get index handle
    index = pc.Index(INDEX_NAME)

    # --- 3) Dense embeddings (Hugging Face) ---
    # Uses sentence-transformers/all-MiniLM-L6-v2 (384 dims)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        # ensure HF token is visible to sentence-transformers
        cache_folder=os.path.join(os.getcwd(), ".hf_cache"),
    )

    # --- 4) Sparse encoder (BM25 = TF-IDF) ---
    bm25 = BM25Encoder()

    # Example corpus
    sentences = [
        "In 2023 I visited Paris.",
        "In 2022 I visited New York.",
        "In 2021 I visited Orlando.",
        "My favorite food in New York was pizza.",
        "The Louvre in Paris was stunning in 2023.",
    ]

    # Fit BM25 on your corpus (important for quality sparse vectors)
    bm25.fit(sentences)

    # (Optional) persist / load sparse model
    # bm25.dump("bm25.json")
    # bm252 = BM25Encoder().load("bm25.json")

    # --- 5) Hybrid retriever (dense + sparse) ---
    retriever = PineconeHybridSearchRetriever(
        embeddings=embeddings,
        sparse_encoder=bm25,
        index=index,
        top_k=3,  # tweak as needed
    )

    # --- 6) Upsert documents ---
    print("Upserting documents...")
    retriever.add_texts(sentences)
    # Give Pinecone a short moment to index
    time.sleep(2)
    print("Upsert complete")

    # --- 7) Testing Code ---
    queries = [
        "What city did I visit last?",
        "Which city did I visit first?",
        "What museum did I see in Paris?",
        "Which place had pizza?",
    ]

    for q in queries:
        print("\n---")
        print(f"Q: {q}")
        docs = retriever.get_relevant_documents(q)
        for i, d in enumerate(docs, 1):
            # 'page_content' holds the original text
            print(f"{i}. {d.page_content}")


if __name__ == "__main__":
    main()
