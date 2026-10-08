"""Tests for data validation and cleaning."""

from __future__ import annotations

from tempfile import TemporaryDirectory
from pathlib import Path

import pandas as pd
import pytest

from src.validation import validate_telemetry, clean_data


def get_valid_record() -> dict:
    """Return a valid telemetry record."""
    return {
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
    }


def test_validate_valid_records():
    """Test validation of valid telemetry records."""
    records = [get_valid_record()]
    df = pd.DataFrame(records)
    result = validate_telemetry(df)
    assert result.valid_rows == 1
    assert result.invalid_rows == 0


def test_validate_missing_required_column():
    """Test validation detects missing required column."""
    record = get_valid_record()
    del record["source_ip"]
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1
    assert "missing_columns" in result.errors or result.invalid_rows > 0


def test_validate_malformed_timestamp():
    """Test validation detects malformed timestamp."""
    record = get_valid_record()
    record["timestamp"] = "not-a-timestamp"
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1
    assert len(result.invalid_records) == 1
    assert any("timestamp" in err for err in result.invalid_records[0]["errors"])


def test_validate_invalid_port():
    """Test validation detects invalid port numbers."""
    record = get_valid_record()
    record["dest_port"] = "invalid_port"
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1
    assert any("port" in err.lower() for err in result.invalid_records[0]["errors"])


def test_validate_negative_bytes():
    """Test validation detects negative byte count."""
    record = get_valid_record()
    record["bytes"] = -500
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1
    assert any("negative" in err.lower() for err in result.invalid_records[0]["errors"])


def test_validate_invalid_label():
    """Test validation detects invalid threat label."""
    record = get_valid_record()
    record["label"] = "UnknownThreat"
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1
    assert any("label" in err.lower() for err in result.invalid_records[0]["errors"])


def test_validate_missing_auth_status():
    """Test validation detects missing auth_status."""
    record = get_valid_record()
    record["auth_status"] = None
    df = pd.DataFrame([record])
    result = validate_telemetry(df)
    assert result.invalid_rows == 1


def test_validate_mixed_valid_invalid():
    """Test validation separates valid and invalid records."""
    valid = get_valid_record()
    invalid = get_valid_record()
    invalid["timestamp"] = "bad-timestamp"
    df = pd.DataFrame([valid, invalid])
    result = validate_telemetry(df)
    assert result.valid_rows == 1
    assert result.invalid_rows == 1
    assert len(result.valid_records) == 1


def test_clean_data():
    """Test data cleaning operations."""
    record = get_valid_record()
    record["protocol"] = "TCP"  # uppercase
    record["auth_status"] = "SUCCESS"  # uppercase
    df = pd.DataFrame([record])
    df_clean = clean_data(df)
    assert df_clean.iloc[0]["protocol"] == "tcp"
    assert df_clean.iloc[0]["auth_status"] == "success"
    assert pd.api.types.is_datetime64_any_dtype(df_clean["timestamp"])


def test_validate_empty_dataframe():
    """Test validation of empty DataFrame."""
    df = pd.DataFrame()
    result = validate_telemetry(df)
    assert result.total_rows == 0
    assert result.valid_rows == 0
    assert result.invalid_rows == 0
