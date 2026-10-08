"""Tests for risk."""
from __future__ import annotations
import pandas as pd
from src.risk_engine import calculate_risk_score, evaluate_policy

def test_risk_range():
    df = pd.DataFrame([{"predicted_threat": "Data Exfiltration", "anomaly_score": 85, "auth_failure_rate": 0.0, "is_scan_pattern": 0, "is_exfil_pattern": 1, "total_bytes_window": 2500000, "unique_dest_ports": 8}])
    result = calculate_risk_score(df)
    assert 0 <= result["risk_score"].iloc[0] <= 100
    assert result["risk_level"].iloc[0] in ["Normal", "Suspicious", "Malicious"]

def test_policy():
    result = evaluate_policy([15, 55, 90], 70)
    assert result["breached"] is True
    assert result["status"] == "failed"
