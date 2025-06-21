import streamlit as st
import requests
import json

st.title("🧠 Local Ollama Chat (Streaming)")

query = st.text_input("Ask something:", placeholder="Type your message here...")

if st.button("Search") and query.strip():
    with st.spinner("Streaming response from Ollama..."):
        try:
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": "llama3",
                "prompt": query,
                "stream": True
            }

            response = requests.post(url, json=payload, stream=True)
            response.raise_for_status()

            st.markdown("### 💬 Response:")
            response_area = st.empty()
            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line.decode("utf-8"))
                        content = json_data.get("response", "")
                        full_response += content
                        response_area.markdown(full_response)
                    except json.JSONDecodeError:
                        continue

        except requests.exceptions.RequestException as e:
            st.error(f"Error: {e}")
else:
    st.caption("Enter a prompt and click 'Search' to stream a response from Ollama.")
