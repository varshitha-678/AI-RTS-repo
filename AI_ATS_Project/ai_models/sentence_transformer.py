"""
Sentence-BERT model for semantic similarity.
"""
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False


class SBERTEmbedder:
    """Generates Sentence-BERT embeddings."""

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        if not SBERT_AVAILABLE:
            raise ImportError("sentence-transformers is required.")
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> np.ndarray:
        return self.model.encode(text, convert_to_numpy=True)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def similarity(self, text1: str, text2: str) -> float:
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return self.cosine_similarity(emb1, emb2)

    def batch_similarity(self, query: str, candidates: list) -> list:
        """Return similarity scores of query vs each candidate."""
        q_emb = self.get_embedding(query)
        scores = []
        for c in candidates:
            c_emb = self.get_embedding(c)
            scores.append(self.cosine_similarity(q_emb, c_emb))
        return scores
