import ollama
from abc import ABC, abstractmethod
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class EmbeddingManager(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> dict:
        pass

    @abstractmethod
    def embed_texts(self, texts: list) -> dict:
        pass

class OllamaEmbeddingManager(EmbeddingManager):
    """Manager for embedding text using Ollama's embedding models.

    Args:
        embedding_model (str): The name of the Ollama embedding model to use.
    """
    def __init__(self, embedding_model: str) -> None:
        self.embedding_model = embedding_model

    def embed_text(self, text: str) -> dict:
        """Convert a text string into a vector."""
        try:
            result = ollama.embed(model=self.embedding_model, input=text)
            vector = result.get("embeddings")[0]
            if vector is None:
                logger.error(f"Failed to embed text: {text}")
                return {}
            return {text: vector}
        except Exception as e:
            raise RuntimeError(f"Ollama embedding error: {e}")

    def embed_texts(self, texts: list) -> dict:
        """Convert a list of texts into vectors."""
        vectors = {}
        try:
            result = ollama.embed(model=self.embedding_model, input=texts)
            embeddings = result.get("embeddings", [])
            for text, vector in zip(texts, embeddings):
                if vector is None:
                    logger.error(f"Failed to embed text: {text}")
                else:
                    vectors[text] = vector
            return vectors
        except Exception as e:
            raise RuntimeError(f"Ollama embedding error: {e}")

class EmbeddingManagerFactory:
    """Factory class to create an instance of EmbeddingManager."""
    @staticmethod
    def create_ollama_embedding_manager(embedding_model: str) -> EmbeddingManager:
        """Create an instance of OllamaEmbeddingManager."""
        return OllamaEmbeddingManager(embedding_model)
