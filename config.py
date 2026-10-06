import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm_model: str = os.getenv("LLM_MODEL", "qwen3:4b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    documents_dir: str = os.getenv("DOCUMENTS_DIR", "./documents")
    chroma_dir: str = os.getenv("CHROMA_DIR", "./chroma_db")

settings = Settings()
