from pathlib import Path
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from app.config import settings

class VectorService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )
        self.store = Chroma(
            collection_name="enterprise_docs",
            persist_directory=settings.chroma_dir,
            embedding_function=self.embeddings,
        )

    def ingest_folder(self, folder: str = "data/docs") -> int:
        docs = []
        for path in Path(folder).glob("*.txt"):
            text = path.read_text(encoding="utf-8")
            chunks = [text[i:i+1200] for i in range(0, len(text), 1000)]
            for idx, chunk in enumerate(chunks):
                docs.append(Document(
                    page_content=chunk,
                    metadata={"source": path.name, "chunk": idx}
                ))
        if docs:
            self.store.add_documents(docs)
        return len(docs)

    def search(self, question: str, limit: int = 4):
        docs = self.store.similarity_search(question, k=limit)
        return [{
            "source_type": "vector",
            "source": d.metadata.get("source", "document"),
            "content": d.page_content,
        } for d in docs]
