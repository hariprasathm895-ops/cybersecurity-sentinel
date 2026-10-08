"""Tests for data ingestion from CSV/JSON files."""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pandas as pd
import pytest

from src.ingestion import load_telemetry, normalize_columns


def test_load_valid_csv():
    """Test loading a valid CSV file."""
    with TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        df_orig = pd.DataFrame({
            "timestamp": ["2026-10-08T10:00:00Z"],
            "source_ip": ["10.0.0.1"],
            "dest_ip": ["10.0.0.2"],
            "src_port": [1234],
            "dest_port": [80],
            "protocol": ["tcp"],
            "bytes": [1000],
            "packets": [5],
            "auth_status": ["success"],
            "event_type": ["http"],
        })
        df_orig.to_csv(csv_path, index=False)

        df = load_telemetry(csv_path)
        assert len(df) == 1
        assert df.iloc[0]["source_ip"] == "10.0.0.1"


def test_load_missing_file():
    """Test error handling for missing file."""
    with pytest.raises(FileNotFoundError):
        load_telemetry("/nonexistent/path/file.csv")


def test_load_empty_file():
    """Test error handling for empty file."""
    with TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "empty.csv"
        csv_path.write_text("")
        with pytest.raises(ValueError, match="empty"):
            load_telemetry(csv_path)


def test_load_csv_with_extra_columns():
    """Test that extra columns are preserved."""
    with TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"
        df_orig = pd.DataFrame({
            "timestamp": ["2026-10-08T10:00:00Z"],
            "source_ip": ["10.0.0.1"],
            "dest_ip": ["10.0.0.2"],
            "src_port": [1234],
            "dest_port": [80],
            "protocol": ["tcp"],
            "bytes": [1000],
            "packets": [5],
            "auth_status": ["success"],
            "event_type": ["http"],
            "extra_field": ["extra_value"],
        })
        df_orig.to_csv(csv_path, index=False)

        df = load_telemetry(csv_path)
        assert "extra_field" in df.columns
        assert df.iloc[0]["extra_field"] == "extra_value"


def test_normalize_columns():
    """Test column name normalization."""
    df = pd.DataFrame({
        "Source IP": ["10.0.0.1"],
        "Dest-IP": ["10.0.0.2"],
        "SrcPort": [1234],
    })
    df_norm = normalize_columns(df)
    assert "source_ip" in df_norm.columns
    assert "dest_ip" in df_norm.columns
    assert "srcport" in df_norm.columns
