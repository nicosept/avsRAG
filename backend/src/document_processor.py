import ollama
from ollama import EmbedResponse
import os
from dotenv import load_dotenv
import logging

load_dotenv()
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

logger = logging.getLogger(__name__)

class processor:
    def __init__(self):
        self.embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")

    def embed_prompt(self, prompt: str) -> dict:
        """Convert a prompt string into a vector."""
        result = ollama.embed(model=self.embedding_model, input=prompt)
        vector = result.get("embeddings")[0]
        if vector is None:
            logger.error(f"Failed to embed prompt: {prompt}")
            return {}
        return {prompt: vector}
    
    def embed_texts(self, texts: list) -> dict:
        """Convert a list of texts into vectors."""
        vectors = {}
        result = ollama.embed(model=self.embedding_model, input=texts)
        embeddings = result.get("embeddings", [])
        print(type(embeddings))
        for text, vector in zip(texts, embeddings):
            if vector is None:
                logger.error(f"Failed to embed text: {text}")
            else:
                vectors[text] = vector
        return vectors
    
    def process_document(self, text: str) -> list:
        """Process a document text into a format suitable for RAG."""
        # Currently splits by sentences, will need to be improved with more advanced NLP techniques
        paragraphs = text.split('\n')
        sentences = [paragraph.split('. ') for paragraph in paragraphs]
        sentences = [sentence.strip() for sublist in sentences for sentence in sublist if sentence.strip()]
        if not sentences:
            raise ValueError("No valid sentences found in the document.")
        logger.info(f"Processed document into {len(sentences)} sentences.")
        return sentences
        