"""Tests for features."""
from __future__ import annotations
import pandas as pd
from src.features import generate_features

def test_feature_generation():
    df = pd.DataFrame([
        {"timestamp": "2026-10-08T10:00:00Z", "source_ip": "10.0.0.1", "dest_ip": "10.0.0.2", "src_port": 1234, "dest_port": 80, "protocol": "tcp", "bytes": 1000, "packets": 5, "auth_status": "success", "event_type": "http"},
        {"timestamp": "2026-10-08T10:00:05Z", "source_ip": "10.0.0.1", "dest_ip": "10.0.0.3", "src_port": 2234, "dest_port": 443, "protocol": "tcp", "bytes": 1200, "packets": 6, "auth_status": "success", "event_type": "https"},
    ])
    result = generate_features(df)
    assert "unique_dest_ips" in result.columns
    assert "connection_rate" in result.columns
    assert len(result) == 2
