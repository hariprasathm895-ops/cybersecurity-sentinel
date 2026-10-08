"""Tests for validation."""
from __future__ import annotations
import pandas as pd
from src.validation import validate_telemetry, clean_data

def test_valid_record():
    df = pd.DataFrame([{
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
    result = validate_telemetry(df)
    assert result.valid_rows == 1

def test_bad_timestamp():
    df = pd.DataFrame([{
        "timestamp": "not-a-date",
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
    result = validate_telemetry(df)
    assert result.invalid_rows == 1

def test_clean():
    df = pd.DataFrame([{
        "timestamp": "2026-10-08T10:00:00Z",
        "source_ip": "10.0.0.1",
        "dest_ip": "10.0.0.2",
        "src_port": "1234",
        "dest_port": "80",
        "protocol": "TCP",
        "bytes": "1000",
        "packets": "5",
        "auth_status": "SUCCESS",
        "event_type": "HTTP",
        "label": "Normal",
    }])
    cleaned = clean_data(df)
    assert cleaned.iloc[0]["protocol"] == "tcp"
    assert cleaned.iloc[0]["auth_status"] == "success"
