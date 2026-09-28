"""
Ensemble ML model combining Random Forest, Logistic Regression, and SVM.
"""
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pickle
import os


class EnsembleATSModel:
    """
    Ensemble model that combines RF, LR, SVM to produce ATS match score.
    When no trained model exists, it uses a weighted heuristic combination.
    """

    MODEL_PATH = os.path.join(os.path.dirname(__file__), "ensemble_model.pkl")

    def __init__(self):
        self.rf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lr = LogisticRegression(max_iter=1000, random_state=42)
        self.svm = SVC(probability=True, kernel="rbf", random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self._try_load()

    def _try_load(self):
        if os.path.exists(self.MODEL_PATH):
            try:
                with open(self.MODEL_PATH, "rb") as f:
                    data = pickle.load(f)
                self.rf = data["rf"]
                self.lr = data["lr"]
                self.svm = data["svm"]
                self.scaler = data["scaler"]
                self.is_trained = True
            except Exception:
                self.is_trained = False

    def save(self):
        with open(self.MODEL_PATH, "wb") as f:
            pickle.dump(
                {"rf": self.rf, "lr": self.lr, "svm": self.svm, "scaler": self.scaler},
                f,
            )

    def build_feature_vector(
        self,
        tfidf_score: float,
        sbert_score: float,
        bert_score: float,
        w2v_score: float,
        keyword_overlap: float,
        skill_overlap: float,
    ) -> np.ndarray:
        return np.array(
            [tfidf_score, sbert_score, bert_score, w2v_score, keyword_overlap, skill_overlap]
        ).reshape(1, -1)

    def train(self, X: np.ndarray, y: np.ndarray):
        X_scaled = self.scaler.fit_transform(X)
        self.rf.fit(X_scaled, y)
        self.lr.fit(X_scaled, y)
        self.svm.fit(X_scaled, y)
        self.is_trained = True
        self.save()

    def predict_score(
        self,
        tfidf_score: float,
        sbert_score: float,
        bert_score: float,
        w2v_score: float,
        keyword_overlap: float,
        skill_overlap: float,
    ) -> float:
        """
        Returns a 0–100 ATS score.
        If model is trained, uses ensemble probability.
        Otherwise, uses weighted average heuristic.
        """
        if self.is_trained:
            features = self.build_feature_vector(
                tfidf_score, sbert_score, bert_score, w2v_score,
                keyword_overlap, skill_overlap
            )
            X_scaled = self.scaler.transform(features)
            probs = []
            for clf in [self.rf, self.lr, self.svm]:
                p = clf.predict_proba(X_scaled)[0]
                probs.append(p[1] if len(p) > 1 else p[0])
            score = np.mean(probs) * 100
        else:
            # Weighted heuristic
            weights = {
                "sbert": 0.30,
                "bert": 0.20,
                "tfidf": 0.20,
                "w2v": 0.10,
                "keyword": 0.10,
                "skill": 0.10,
            }
            score = (
                sbert_score * weights["sbert"]
                + bert_score * weights["bert"]
                + tfidf_score * weights["tfidf"]
                + w2v_score * weights["w2v"]
                + keyword_overlap * weights["keyword"]
                + skill_overlap * weights["skill"]
            ) * 100

        return min(max(round(score, 2), 0), 100)

    def evaluate(self, X: np.ndarray, y: np.ndarray) -> dict:
        if not self.is_trained:
            return {}
        X_scaled = self.scaler.transform(X)
        # Use voting
        preds_rf = self.rf.predict(X_scaled)
        preds_lr = self.lr.predict(X_scaled)
        preds_svm = self.svm.predict(X_scaled)
        # Majority vote
        preds = np.round((preds_rf + preds_lr + preds_svm) / 3).astype(int)
        return {
            "accuracy": round(accuracy_score(y, preds), 4),
            "precision": round(precision_score(y, preds, zero_division=0), 4),
            "recall": round(recall_score(y, preds, zero_division=0), 4),
            "f1_score": round(f1_score(y, preds, zero_division=0), 4),
        }
