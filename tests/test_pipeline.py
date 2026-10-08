"""Tests for pipeline."""
from __future__ import annotations
from pathlib import Path
import pandas as pd
from src.pipeline import run_pipeline

def test_pipeline(tmp_path):
    data = pd.DataFrame([{
        "timestamp": "2026-10-08T10:00:00Z",
        "source_ip": "10.0.0.1",
        "dest_ip": "10.0.0.2",
        "src_port": 1234,
        "dest_port": 80,
        "protocol": "tcp",
        "bytes": 1000,
        "packets": 5,
        "auth_status": "success",
        "event_type": "http",
        "label": "Normal",
    }])
    csv_path = tmp_path / "test.csv"
    data.to_csv(csv_path, index=False)
    exit_code = run_pipeline(str(csv_path), max_risk=90)
    assert exit_code in [0, 1]
