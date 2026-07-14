from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # FastAPI Server settings
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Gemini API Credentials
    GEMINI_API_KEY: Optional[str] = None
    
    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIR: str = "./data/chromadb"
    
    # Pydantic Settings configuration to load from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
