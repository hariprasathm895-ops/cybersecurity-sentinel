"""Risk scoring engine."""
from __future__ import annotations
import logging
import pandas as pd
logger = logging.getLogger(__name__)

THREAT_SCORES = {
    "Normal": 10,
    "Port Scan": 70,
    "Brute Force": 80,
    "Lateral Movement": 75,
    "Data Exfiltration": 90,
}

def _get_risk_level(score: float) -> str:
    if score <= 30:
        return "Normal"
    if score <= 70:
        return "Suspicious"
    return "Malicious"

def calculate_risk_score(df: pd.DataFrame, max_risk: int = 100) -> pd.DataFrame:
    result = df.copy()
    if result.empty:
        result["risk_score"] = []
        result["risk_level"] = []
        return result
    for idx, row in result.iterrows():
        threat = str(row.get("predicted_threat", "Normal"))
        base = THREAT_SCORES.get(threat, 10)
        anomaly = float(row.get("anomaly_score", 0) or 0)
        auth_fail = float(row.get("auth_failure_rate", 0) or 0)
        is_scan = int(row.get("is_scan_pattern", 0) or 0)
        is_exfil = int(row.get("is_exfil_pattern", 0) or 0)
        bytes_w = float(row.get("total_bytes_window", 0) or 0)
        ports = float(row.get("unique_dest_ports", 0) or 0)
        risk = base + (anomaly / 100.0) * 25 + min(auth_fail * 100, 25) * 0.3 + is_scan * 10 + is_exfil * 12 + min(bytes_w / 2000000.0, 1.0) * 10 + min(ports / 50.0, 1.0) * 5
        risk = max(0.0, min(100.0, risk))
        result.at[idx, "risk_score"] = round(risk, 2)
        result.at[idx, "risk_level"] = _get_risk_level(risk)
    return result

def evaluate_policy(risk_scores: list[float], max_risk: int) -> dict:
    scores = [float(s) for s in risk_scores if s is not None]
    if not scores:
        return {"breached": False, "status": "passed", "max_risk": max_risk, "max_score": 0.0}
    max_score = max(scores)
    breached = max_score > max_risk
    return {"breached": breached, "status": "failed" if breached else "passed", "max_risk": max_risk, "max_score": round(max_score, 2)}
