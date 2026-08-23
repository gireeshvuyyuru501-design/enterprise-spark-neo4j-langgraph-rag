from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from app.config import settings
from app.agents.state import RAGState
from app.services.neo4j_service import Neo4jService
from app.services.vector_service import VectorService

def classify(state: RAGState):
    q = state["question"].lower()
    graph_terms = ["employee", "department", "project", "skill", "works", "team", "relationship"]
    route = "hybrid" if any(t in q for t in graph_terms) else "vector"
    return {"route": route}

def graph_retrieve(state: RAGState):
    if state["route"] not in ("graph", "hybrid"):
        return {"graph_sources": []}
    svc = Neo4jService()
    try:
        return {"graph_sources": svc.search(state["question"], state["top_k"])}
    finally:
        svc.close()

def vector_retrieve(state: RAGState):
    try:
        rows = VectorService().search(state["question"], state["top_k"])
    except Exception:
        rows = []
    return {"vector_sources": rows}

def merge_sources(state: RAGState):
    merged = state.get("graph_sources", []) + state.get("vector_sources", [])
    return {"sources": merged[: max(state["top_k"] * 2, 4)]}

def generate(state: RAGState):
    sources = state.get("sources", [])
    context = "\n\n".join(
        f"[{x['source_type']}:{x['source']}]\n{x['content']}" for x in sources
    )

    if not settings.openai_api_key:
        return {"answer": "OPENAI_API_KEY is not configured. Retrieved context:\n\n" + (context or "No context found.")}

    llm = ChatOpenAI(
        model=settings.openai_model,
        temperature=0,
        api_key=settings.openai_api_key,
    )
    prompt = f"""You are an enterprise GraphRAG assistant.
Use only the supplied context. If the answer is missing, say so.
Cite sources inline using [graph:neo4j] or [vector:file].

Question:
{state['question']}

Context:
{context}
"""
    return {"answer": llm.invoke(prompt).content}

def build_graph():
    workflow = StateGraph(RAGState)
    workflow.add_node("classify", classify)
    workflow.add_node("graph_retrieve", graph_retrieve)
    workflow.add_node("vector_retrieve", vector_retrieve)
    workflow.add_node("merge_sources", merge_sources)
    workflow.add_node("generate", generate)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "graph_retrieve")
    workflow.add_edge("graph_retrieve", "vector_retrieve")
    workflow.add_edge("vector_retrieve", "merge_sources")
    workflow.add_edge("merge_sources", "generate")
    workflow.add_edge("generate", END)
    return workflow.compile()

rag_graph = build_graph()

def answer(question: str, top_k: int):
    return rag_graph.invoke({"question": question, "top_k": top_k})
