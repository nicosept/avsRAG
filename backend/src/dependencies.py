from backend.src.vector_store import vector_store
from backend.src.embedding_manager import EmbeddingManagerFactory
import os

EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

store = vector_store()
embedding_manager = EmbeddingManagerFactory.create_ollama_embedding_manager(EMBEDDING_MODEL)