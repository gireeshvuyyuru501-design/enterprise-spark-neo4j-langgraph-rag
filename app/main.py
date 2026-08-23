from fastapi import FastAPI, HTTPException, Query
from app.config import settings
from app.models import AskRequest, AskResponse, IngestResponse
from app.agents.graph import answer as rag_answer
from app.services.vector_service import VectorService
from app.services.neo4j_service import Neo4jService
from app.db.history import init_db, save_question, list_questions

app = FastAPI(title="Enterprise Spark Neo4j LangGraph RAG", version="1.0.0")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    neo4j_ok = False
    try:
        svc = Neo4jService()
        neo4j_ok = svc.health()
        svc.close()
    except Exception:
        pass
    return {"status": "ok", "neo4j": neo4j_ok}

@app.post("/ingest", response_model=IngestResponse)
def ingest():
    try:
        indexed = VectorService().ingest_folder("data/docs")
        return {"status": "ok", "indexed": indexed}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        result = rag_answer(request.question, request.top_k or settings.top_k)
        save_question(request.question, result["answer"], result["route"])
        return {
            "answer": result["answer"],
            "route": result["route"],
            "sources": result.get("sources", []),
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

@app.get("/questions")
def questions(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    items, total = list_questions(limit, offset)
    return {"items": items, "total": total}
