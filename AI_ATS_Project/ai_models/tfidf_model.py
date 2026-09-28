"""
TF-IDF and Word2Vec feature extraction models.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine

try:
    from gensim.models import Word2Vec
    GENSIM_AVAILABLE = True
except ImportError:
    GENSIM_AVAILABLE = False


class TFIDFModel:
    """TF-IDF based similarity."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))

    def fit_transform(self, corpus: list):
        return self.vectorizer.fit_transform(corpus)

    def similarity(self, text1: str, text2: str) -> float:
        tfidf_matrix = self.fit_transform([text1, text2])
        score = sk_cosine(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(score)

    def get_top_terms(self, text: str, top_n: int = 20) -> list:
        tfidf_matrix = self.vectorizer.fit_transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]
        top_indices = scores.argsort()[-top_n:][::-1]
        return [(feature_names[i], scores[i]) for i in top_indices if scores[i] > 0]


class Word2VecModel:
    """Word2Vec based document similarity."""

    def __init__(self, vector_size=100, window=5, min_count=1):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.model = None

    def train(self, tokenized_corpus: list):
        if not GENSIM_AVAILABLE:
            raise ImportError("gensim is required for Word2Vec.")
        self.model = Word2Vec(
            sentences=tokenized_corpus,
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=4,
        )

    def get_document_vector(self, tokens: list) -> np.ndarray:
        if self.model is None:
            return np.zeros(self.vector_size)
        vectors = [
            self.model.wv[token]
            for token in tokens
            if token in self.model.wv
        ]
        if not vectors:
            return np.zeros(self.vector_size)
        return np.mean(vectors, axis=0)

    def similarity(self, tokens1: list, tokens2: list) -> float:
        vec1 = self.get_document_vector(tokens1)
        vec2 = self.get_document_vector(tokens2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
