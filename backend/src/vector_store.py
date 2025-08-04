# Future work: Implement an interface for non-Ollama models and postgreSQL or other vector stores.

class vector_store:
    """
    A simple vector store to manage vectors for RAG (Retrieval-Augmented Generation).
    """

    def __init__(self):
        self.store = {}

    def add_vectors(self, vectors: dict):
        """Add multiple vectors to the store."""
        for key, vector in vectors.items():
            self.store[key] = vector

    def get_vector(self, key: str) -> list:
        """Retrieve a vector from the store."""
        return self.store.get(key, None)

    def clear_store(self):
        """Clear the vector store."""
        self.store.clear()

    def search_vectors(self, query_vector: dict, top_k: int = 5, threshold: float = 0.5) -> list:
        """Search for the most similar vectors in the store."""
        cosine_similarities = []
        query_vector = list(query_vector.values())[0] 
        for key, vector in self.store.items():
            similarity = self.cosine_similarity(query_vector, vector)
            cosine_similarities.append((key, similarity))

        # Return the top_k results
        top_k = sorted(cosine_similarities, key=lambda x: x[1], reverse=True)[:top_k]
        # Filter results based on the threshold
        thresholded_results = [key for key, similarity in top_k if similarity >= threshold]
        return thresholded_results

    def cosine_similarity(self, vector_a: list, vector_b: list) -> float:
        """Compute the cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vector_a, vector_b))
        norm_a = sum(a ** 2 for a in vector_a) ** 0.5
        norm_b = sum(b ** 2 for b in vector_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
    

