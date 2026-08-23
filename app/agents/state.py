from typing import TypedDict, List, Dict

class RAGState(TypedDict, total=False):
    question: str
    top_k: int
    route: str
    graph_sources: List[Dict]
    vector_sources: List[Dict]
    sources: List[Dict]
    answer: str
