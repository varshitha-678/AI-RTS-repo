"""
BERT-based embedding model for semantic similarity.
"""
import numpy as np

try:
    from transformers import BertTokenizer, BertModel
    import torch
    BERT_AVAILABLE = True
except ImportError:
    BERT_AVAILABLE = False


class BERTEmbedder:
    """Generates BERT embeddings for text."""

    def __init__(self, model_name="bert-base-uncased"):
        if not BERT_AVAILABLE:
            raise ImportError("transformers and torch are required.")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()

    def get_embedding(self, text: str) -> np.ndarray:
        """Return mean-pooled BERT embedding for input text."""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Mean pool over token embeddings
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
        return embedding

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    def similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return self.cosine_similarity(emb1, emb2)
