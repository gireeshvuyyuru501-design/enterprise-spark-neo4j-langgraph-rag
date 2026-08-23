from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password12345"
    chroma_dir: str = "./chroma_db"
    sqlite_path: str = "./questions.db"
    top_k: int = 4
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
