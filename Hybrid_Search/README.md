# Hybrid Search with Pinecone, LangChain, and Hugging Face

## Overview
This proof-of-concept demonstrates a **Hybrid Search** system that combines:
- **Semantic Search** (dense vector embeddings using Hugging Face Sentence Transformers)
- **Syntactic/Keyword Search** (sparse vector search using BM25/TF-IDF)

The backend is powered by:
- **[Pinecone](https://www.pinecone.io/)** for vector storage and retrieval
- **[LangChain](https://www.langchain.com/)** for retriever orchestration
- **[Hugging Face](https://huggingface.co/)** for sentence embeddings
- **BM25/TF-IDF** for keyword-based matching

The hybrid approach leverages the strengths of both semantic and syntactic search for improved retrieval accuracy.

---

## Features
- Create a Pinecone **serverless** index programmatically
- Generate **dense embeddings** using the Hugging Face model `all-MiniLM-L6-v2` (384-dimensional vectors)
- Generate **sparse vectors** using BM25 (TF-IDF-based keyword scoring)
- Store and retrieve data using Pinecone's **hybrid search**
- Run example queries and retrieve relevant results ranked by combined scores

---

## What is Semantic Search?
Semantic search focuses on **meaning** rather than exact keyword matches.  
In this project:
- Text is converted into **dense vectors** using a sentence transformer.
- Similarity between queries and documents is calculated using vector similarity metrics (dot product, cosine similarity).
- Useful when the query uses **different words but similar meaning** to the target text.

Example:
> Query: "Capital of France"  
> Match: "Paris is the capital city of France"  
Even if the word "capital" isn't matched exactly, the semantic meaning is understood.

---

## What is Syntactic (Keyword) Search?
Syntactic search focuses on **exact term matches** between the query and documents.  
In this project:
- BM25 is used as the sparse encoder.
- Relies on **TF-IDF** (Term Frequency – Inverse Document Frequency) weighting.
- Useful when **exact keyword matching** is critical.

Example:
> Query: "visited Paris 2023"  
> Match: "In 2023 I visited Paris"  
This works because the words match exactly.

---

## Cosine Similarity
Cosine similarity measures the **cosine of the angle** between two vectors in a multi-dimensional space.
- Value ranges from **-1 to 1**.
- **1** means vectors are identical in direction.
- **0** means they are orthogonal (no similarity).
- **-1** means they are diametrically opposed.

In semantic search:
- Each document and query is embedded into a dense vector.
- Cosine similarity measures how close they are in meaning.

Formula:
```
cosine_similarity = (A • B) / (||A|| * ||B||)
```
Where:
- `A • B` is the dot product of vectors A and B
- `||A||` and `||B||` are the magnitudes of A and B

---

## TF-IDF
TF-IDF is a statistical measure used to evaluate how important a word is to a document in a collection.
- **TF (Term Frequency):** Measures how often a term appears in a document.
- **IDF (Inverse Document Frequency):** Reduces the weight of terms that appear frequently across many documents (common words like "the", "and").

Formula:
```
TF-IDF(term, doc) = TF(term, doc) * log(N / DF(term))
```
Where:
- `TF(term, doc)` is the frequency of the term in the document
- `N` is the total number of documents
- `DF(term)` is the number of documents containing the term

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/hybrid-search-poc.git
cd hybrid-search-poc
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Variables
Create a `.env` file in the project root with:
```
PINECONE_API_KEY=your_pinecone_api_key
HF_TOKEN=your_huggingface_api_token
```

---

## Running the Project
```bash
python main.py
```
This will:
- Create or connect to a Pinecone index
- Generate both dense and sparse vectors
- Insert sample documents
- Run example hybrid queries

---

## Requirements File
Example `requirements.txt`:
```txt
python-dotenv>=1.0.1
numpy>=1.26.0
pinecone>=5.0.0
pinecone-text>=0.9.0
pinecone-notebooks
langchain>=0.2.12
langchain-community>=0.2.10
langchain-huggingface>=0.0.3
sentence-transformers>=2.2.2
```

---

## References
- [Pinecone Documentation](https://docs.pinecone.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [Hugging Face Transformers](https://huggingface.co/sentence-transformers)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)
