from pydantic import BaseModel, Field
from typing import List, Optional

class AskRequest(BaseModel):
    question: str = Field(min_length=2)
    top_k: Optional[int] = Field(default=None, ge=1, le=20)

class SourceItem(BaseModel):
    source_type: str
    source: str
    content: str

class AskResponse(BaseModel):
    answer: str
    route: str
    sources: List[SourceItem]

class IngestResponse(BaseModel):
    status: str
    indexed: int
