# Enterprise Spark + Neo4j + LangGraph Hybrid RAG

Portfolio-ready enterprise AI project using PySpark, Neo4j, LangGraph, Chroma, FastAPI, Streamlit, and SQLite.

## Flow

CSV data -> PySpark ETL -> Neo4j Knowledge Graph
TXT docs -> Embeddings -> Chroma Vector Store
User -> Streamlit -> FastAPI -> LangGraph -> Graph + Vector Retrieval -> LLM Answer

See `COMMANDS_WINDOWS.txt` for Windows PowerShell commands.
