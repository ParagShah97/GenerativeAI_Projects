import streamlit as st
import tempfile

from pdf_rag_utils import (
    extract_text_from_the_pdf,
    text_splitter,
    get_documents,
    embed_and_store,
    create_model
)


st.title("📄 PDF Q&A with Ollama + Chroma")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Store the vector store and chain across reruns
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
    st.session_state.chain = None
    st.session_state.text = None

if uploaded_file is not None:
    with st.spinner("🔍 Reading and processing PDF..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        # Run pipeline
        if not st.session_state.text:
            st.session_state.text = extract_text_from_the_pdf(tmp_path)
            chunks = text_splitter(st.session_state.text)
            # documents = get_documents(chunks)
            print("How many time this is running?")
            st.session_state.vector_store = embed_and_store(chunks)
            st.session_state.chain = create_model()
            print("Vector store loaded")

    st.success("✅ PDF processed! Now enter a question.")

# Question input + search button
if st.session_state.vector_store:
    question = st.text_input("Ask a question about the PDF:")
    search_button = st.button("🔍 Search")

    if search_button and question.strip():
        with st.spinner("🤖 Generating answer..."):
            retriever = st.session_state.vector_store.as_retriever(search_kwargs={"k": 3})
            docs = retriever.invoke(question)
            combined = "\n\n".join([doc.page_content for doc in docs])
            result = st.session_state.chain.invoke({"content": combined, "question": question})

            st.markdown("### 💬 Answer:")
            st.write(result)
