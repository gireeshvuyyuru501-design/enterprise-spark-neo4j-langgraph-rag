import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Enterprise GraphRAG", layout="wide")
st.title("Enterprise Spark + Neo4j + LangGraph RAG")
st.caption("Hybrid Graph + Vector Retrieval")

with st.sidebar:
    top_k = st.slider("Top K", 1, 10, 4)
    if st.button("Ingest documents"):
        try:
            r = requests.post(f"{API_URL}/ingest", timeout=120)
            st.write(r.json())
        except Exception as e:
            st.error(str(e))

question = st.text_input(
    "Ask a question",
    placeholder="Which employees know Spark and what projects are they working on?"
)

if st.button("Ask") and question:
    try:
        r = requests.post(
            f"{API_URL}/ask",
            json={"question": question, "top_k": top_k},
            timeout=120,
        )
        data = r.json()
        if r.ok:
            st.subheader("Answer")
            st.write(data["answer"])
            st.info(f"Route: {data['route']}")
            st.subheader("Sources")
            for src in data.get("sources", []):
                with st.expander(f"{src['source_type']} • {src['source']}"):
                    st.write(src["content"])
        else:
            st.error(data)
    except Exception as e:
        st.error(str(e))
