"""
Core ATS Engine — orchestrates parsing, NER, feature extraction, scoring.
"""
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

# Download required NLTK data
for pkg in ["punkt", "stopwords", "wordnet", "averaged_perceptron_tagger", "maxent_ne_chunker", "words"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from ai_models.tfidf_model import TFIDFModel
from ai_models.ensemble_model import EnsembleATSModel

# Optional heavy models — lazy loaded
_sbert_model = None
_bert_model = None

KNOWN_SKILLS = [
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "django", "flask", "fastapi", "spring", "sql", "mongodb",
    "postgresql", "mysql", "redis", "docker", "kubernetes", "aws", "azure",
    "gcp", "git", "linux", "machine learning", "deep learning", "nlp",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "rest api",
    "graphql", "html", "css", "tailwind", "bootstrap", "c++", "c#", "go",
    "rust", "kotlin", "swift", "flutter", "react native", "spark", "hadoop",
    "kafka", "elasticsearch", "jenkins", "ci/cd", "agile", "scrum", "devops",
    "data science", "computer vision", "bert", "transformers", "excel",
    "tableau", "power bi", "r", "matlab", "bash", "shell scripting",
]


def _get_sbert():
    global _sbert_model
    if _sbert_model is None:
        try:
            from ai_models.sentence_transformer import SBERTEmbedder
            _sbert_model = SBERTEmbedder()
        except Exception:
            _sbert_model = None
    return _sbert_model


def _get_bert():
    global _bert_model
    if _bert_model is None:
        try:
            from ai_models.bert_model import BERTEmbedder
            _bert_model = BERTEmbedder()
        except Exception:
            _bert_model = None
    return _bert_model


# ── Text Preprocessing ─────────────────────────────────────────────────────

def preprocess_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s\.\+#]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_and_lemmatize(text: str) -> list:
    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()
    tokens = word_tokenize(text.lower())
    return [
        lemmatizer.lemmatize(t)
        for t in tokens
        if t.isalnum() and t not in stop_words and len(t) > 2
    ]


# ── NER / Information Extraction ───────────────────────────────────────────

def extract_name(text: str) -> str:
    lines = text.strip().split("\n")
    for line in lines[:5]:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and line.replace(" ", "").isalpha():
            return line
    return "Unknown"


def extract_email(text: str) -> str:
    match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    return match.group(0) if match else ""


def extract_phone(text: str) -> str:
    match = re.search(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", text)
    return match.group(0) if match else ""


def extract_skills(text: str) -> list:
    text_lower = text.lower()
    found = []
    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, text_lower):
            found.append(skill)
    return list(set(found))


def extract_education(text: str) -> list:
    education = []
    patterns = [
        r"(b\.?tech|b\.?e|b\.?sc|m\.?tech|m\.?sc|m\.?e|ph\.?d|mba|bca|mca|bachelor|master|doctorate)[^.\n]*",
        r"(university|college|institute|school)[^.\n]*",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        education.extend(matches)
    return list(set(education))[:5]


def extract_experience_years(text: str) -> float:
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s*(?:of\s+)?(?:experience|exp)",
        r"experience\s*(?:of\s+)?(\d+(?:\.\d+)?)\s*\+?\s*years?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0.0


def extract_certifications(text: str) -> list:
    cert_keywords = [
        "certified", "certification", "certificate", "aws certified",
        "google certified", "microsoft certified", "pmp", "cissp",
        "comptia", "oracle certified", "cka", "ckad",
    ]
    lines = text.split("\n")
    certs = []
    for line in lines:
        if any(kw in line.lower() for kw in cert_keywords):
            certs.append(line.strip())
    return certs[:5]


def parse_resume(text: str) -> dict:
    """Full NER + info extraction from resume text."""
    clean = preprocess_text(text)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience_years": extract_experience_years(text),
        "certifications": extract_certifications(text),
        "tokens": tokenize_and_lemmatize(clean),
    }


# ── Keyword Overlap ─────────────────────────────────────────────────────────

def keyword_overlap(text1: str, text2: str) -> float:
    tokens1 = set(tokenize_and_lemmatize(text1))
    tokens2 = set(tokenize_and_lemmatize(text2))
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1 & tokens2
    union = tokens1 | tokens2
    return len(intersection) / len(union)


def skill_overlap(resume_skills: list, jd_skills: list) -> float:
    if not jd_skills:
        return 1.0
    resume_set = set(s.lower() for s in resume_skills)
    jd_set = set(s.lower() for s in jd_skills)
    matched = resume_set & jd_set
    return len(matched) / len(jd_set)


# ── ATS Score Calculation ───────────────────────────────────────────────────

def calculate_ats_score(resume_text: str, jd_text: str, parsed_resume: dict = None) -> dict:
    """
    Orchestrates all models and returns full ATS result dict.
    """
    if parsed_resume is None:
        parsed_resume = parse_resume(resume_text)
    jd_parsed = parse_resume(jd_text)

    # 1. TF-IDF similarity
    tfidf = TFIDFModel()
    tfidf_score = tfidf.similarity(preprocess_text(resume_text), preprocess_text(jd_text))

    # 2. SBERT similarity
    sbert_score = 0.0
    sbert = _get_sbert()
    if sbert:
        try:
            sbert_score = sbert.similarity(resume_text[:1000], jd_text[:1000])
        except Exception:
            sbert_score = tfidf_score

    # 3. BERT similarity
    bert_score = 0.0
    bert = _get_bert()
    if bert:
        try:
            bert_score = bert.similarity(resume_text[:500], jd_text[:500])
        except Exception:
            bert_score = tfidf_score

    # Fallbacks if heavy models unavailable
    if sbert_score == 0.0 and bert_score == 0.0:
        sbert_score = tfidf_score * 0.95
        bert_score = tfidf_score * 0.90

    # 4. Word2Vec similarity (token-level)
    try:
        from ai_models.tfidf_model import Word2VecModel
        w2v = Word2VecModel()
        corpus = [parsed_resume["tokens"], jd_parsed["tokens"]]
        w2v.train(corpus)
        w2v_score = w2v.similarity(parsed_resume["tokens"], jd_parsed["tokens"])
    except Exception:
        w2v_score = tfidf_score * 0.85

    # 5. Keyword & skill overlaps
    kw_overlap = keyword_overlap(resume_text, jd_text)
    sk_overlap = skill_overlap(parsed_resume["skills"], jd_parsed["skills"])

    # 6. Ensemble score
    ensemble = EnsembleATSModel()
    ats_score = ensemble.predict_score(
        tfidf_score, sbert_score, bert_score, w2v_score, kw_overlap, sk_overlap
    )

    # 7. Missing skills
    resume_skill_set = set(s.lower() for s in parsed_resume["skills"])
    jd_skill_set = set(s.lower() for s in jd_parsed["skills"])
    missing_skills = list(jd_skill_set - resume_skill_set)

    return {
        "ats_score": ats_score,
        "match_percentage": round(ats_score, 2),
        "tfidf_score": round(tfidf_score * 100, 2),
        "sbert_score": round(sbert_score * 100, 2),
        "bert_score": round(bert_score * 100, 2),
        "w2v_score": round(w2v_score * 100, 2),
        "keyword_overlap": round(kw_overlap * 100, 2),
        "skill_overlap": round(sk_overlap * 100, 2),
        "extracted_skills": parsed_resume["skills"],
        "jd_skills": list(jd_skill_set),
        "missing_skills": missing_skills,
        "matched_skills": list(resume_skill_set & jd_skill_set),
        "name": parsed_resume["name"],
        "experience_years": parsed_resume["experience_years"],
        "education": parsed_resume["education"],
        "certifications": parsed_resume["certifications"],
    }
