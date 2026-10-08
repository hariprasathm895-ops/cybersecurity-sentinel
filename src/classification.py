"""Classification using Random Forest."""
from __future__ import annotations
import logging
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from config import CLASSIFIER_MODEL_PATH, THREAT_LABELS
logger = logging.getLogger(__name__)

def _prep_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df.copy()
    for col in ["timestamp", "label", "source_ip", "dest_ip", "protocol", "auth_status", "event_type", "predicted_threat", "anomaly_score", "is_anomaly"]:
        if col in X.columns:
            X = X.drop(columns=[col])
    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            X[col] = pd.factorize(X[col])[0]
    return X.apply(pd.to_numeric, errors="coerce").fillna(0)

def train_classifier(df: pd.DataFrame, model_path: Path | str | None = None) -> dict:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    if df is None or df.empty or "label" not in df.columns:
        raise ValueError("Need labeled data")
    model_path = Path(model_path or CLASSIFIER_MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    labeled = df[df["label"].notna()]
    if labeled.empty:
        raise ValueError("No labeled records")
    X = _prep_features(labeled)
    y = labeled["label"].astype(str)
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
    model.fit(X, y)
    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    joblib.dump(model, model_path)
    logger.info(f"Classifier saved to {model_path} (accuracy={acc:.3f})")
    return {"accuracy": float(acc), "labels": list(model.classes_)}

def classify_threats(df: pd.DataFrame, model_path: Path | str | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return df.copy()
    model_path = Path(model_path or CLASSIFIER_MODEL_PATH)
    if not model_path.exists():
        if "label" in df.columns:
            train_classifier(df, model_path)
        else:
            df = df.copy()
            df["predicted_threat"] = "Normal"
            df["threat_confidence"] = 0.5
            return df
    model = joblib.load(model_path)
    X = _prep_features(df)
    preds = model.predict(X)
    probs = model.predict_proba(X).max(axis=1)
    result = df.copy()
    result["predicted_threat"] = preds
    result["threat_confidence"] = probs.round(3)
    return result
