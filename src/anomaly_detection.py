"""Anomaly detection using Isolation Forest."""
from __future__ import annotations
import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from config import ANOMCALY_MODEL_PATH
logger = logging.getLogger(__name__)

def _prep_features(df: pd.DataFrame) -> pd.DataFrame:
    X = df.copy()
    for col in ["timestamp", "label", "source_ip", "dest_ip", "protocol", "auth_status", "event_type", "predicted_threat"]:
        if col in X.columns:
            X = X.drop(columns=[col])
    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            X[col] = pd.factorize(X[col])[0]
    return X.apply(pd.to_numeric, errors="coerce").fillna(0)

def train_anomaly_detector(df: pd.DataFrame, model_path: Path | str | None = None) -> None:
    from sklearn.ensemble import IsolationForest
    if df is None or df.empty:
        raise ValueError("Need data to train")
    model_path = Path(model_path or ANOMCALY_MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    X = _prep_features(df)
    if X.empty:
        raise ValueError("No features")
    model = IsolationForest(contamination=0.1, n_estimators=100, random_state=42)
    model.fit(X)
    joblib.dump(model, model_path)
    logger.info(f"Anomaly model saved to {model_path}")

def detect_anomalies(df: pd.DataFrame, model_path: Path | str | None = None) -> pd.DataFrame:
    if df is None or df.empty:
        return df.copy()
    model_path = Path(model_path or ANOMCALY_MODEL_PATH)
    if not model_path.exists():
        train_anomaly_detector(df, model_path)
    model = joblib.load(model_path)
    X = _prep_features(df)
    pred = model.predict(X)
    scores = -model.score_samples(X)
    scores = np.clip((scores - scores.min()) / (scores.max() - scores.min() + 1e-9), 0, 1) * 100
    result = df.copy()
    result["anomaly_score"] = scores.round(2)
    result["is_anomaly"] = pred == -1
    return result
