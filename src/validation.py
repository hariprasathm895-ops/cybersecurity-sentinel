"""Validation and cleaning of telemetry data."""
from __future__ import annotations
import logging
from typing import Any
import pandas as pd
from config import REQUIRED_COLUMNS, THREAT_LABELS
logger = logging.getLogger(__name__)

class ValidationResult:
    def __init__(self):
        self.valid_records: pd.DataFrame = pd.DataFrame()
        self.invalid_records: list[dict] = []
        self.errors: dict[str, Any] = {}
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.invalid_rows: int = 0
    def __repr__(self) -> str:
        return f"ValidationResult(total={self.total_rows}, valid={self.valid_rows}, invalid={self.invalid_rows})"

def validate_telemetry(df: pd.DataFrame) -> ValidationResult:
    result = ValidationResult()
    if df is None or df.empty:
        return result
    result.total_rows = len(df)
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        result.errors["missing_columns"] = missing_cols
        logger.error(f"Missing required columns: {missing_cols}")
        result.valid_rows = 0
        result.invalid_rows = result.total_rows
        return result
    valid_indices = []
    for idx, row in df.iterrows():
        errors = []
        try:
            pd.to_datetime(row.get("timestamp"))
        except:
            errors.append("bad timestamp")
        if pd.isna(row.get("source_ip")) or str(row.get("source_ip", "")).strip() == "":
            errors.append("missing source_ip")
        if pd.isna(row.get("dest_ip")) or str(row.get("dest_ip", "")).strip() == "":
            errors.append("missing dest_ip")
        try:
            port = int(row.get("src_port", 0))
            if port < 0 or port > 65535:
                errors.append(f"src_port {port} out of range")
        except:
            errors.append("bad src_port")
        try:
            port = int(row.get("dest_port", 0))
            if port < 0 or port > 65535:
                errors.append(f"dest_port {port} out of range")
        except:
            errors.append("bad dest_port")
        try:
            b = float(row.get("bytes", 0))
            if b < 0:
                errors.append("negative bytes")
        except:
            errors.append("bad bytes")
        try:
            p = float(row.get("packets", 0))
            if p < 0:
                errors.append("negative packets")
        except:
            errors.append("bad packets")
        if not errors:
            valid_indices.append(idx)
    result.valid_records = df.loc[valid_indices].reset_index(drop=True) if valid_indices else pd.DataFrame(columns=df.columns)
    result.valid_rows = len(valid_indices)
    result.invalid_rows = result.total_rows - result.valid_rows
    return result

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        return df
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for col in ["src_port", "dest_port", "bytes", "packets"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    for col in ["auth_status", "event_type", "protocol"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.lower()
    logger.info(f"Cleaned {len(df)} records")
    return df
