"""
Unified embeddings utility — lazy loads SBERT / BERT.
"""
import numpy as np
from ai_models.tfidf_model import TFIDFModel

_sbert = None
_bert = None


def get_sbert_similarity(text1: str, text2: str) -> float:
    global _sbert
    if _sbert is None:
        try:
            from ai_models.sentence_transformer import SBERTEmbedder
            _sbert = SBERTEmbedder()
        except Exception:
            return 0.0
    return _sbert.similarity(text1[:1000], text2[:1000])


def get_bert_similarity(text1: str, text2: str) -> float:
    global _bert
    if _bert is None:
        try:
            from ai_models.bert_model import BERTEmbedder
            _bert = BERTEmbedder()
        except Exception:
            return 0.0
    return _bert.similarity(text1[:500], text2[:500])


def get_tfidf_similarity(text1: str, text2: str) -> float:
    tfidf = TFIDFModel()
    return tfidf.similarity(text1, text2)


def get_combined_similarity(text1: str, text2: str) -> dict:
    tfidf = get_tfidf_similarity(text1, text2)
    sbert = get_sbert_similarity(text1, text2) or tfidf
    bert = get_bert_similarity(text1, text2) or tfidf
    combined = (tfidf * 0.3 + sbert * 0.4 + bert * 0.3)
    return {
        "tfidf": round(tfidf, 4),
        "sbert": round(sbert, 4),
        "bert": round(bert, 4),
        "combined": round(combined, 4),
    }
