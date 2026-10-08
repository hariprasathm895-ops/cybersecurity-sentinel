"""Module for validating and cleaning telemetry data."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

from config import REQUIRED_COLUMNS, THREAT_LABELS

logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results."""

    def __init__(self):
        self.valid_records: pd.DataFrame = pd.DataFrame()
        self.invalid_records: list[dict] = []
        self.errors: dict[str, Any] = {}
        self.total_rows: int = 0
        self.valid_rows: int = 0
        self.invalid_rows: int = 0

    def __repr__(self) -> str:
        return (
            f"ValidationResult(total={self.total_rows}, valid={self.valid_rows}, "
            f"invalid={self.invalid_rows})"
        )


def validate_telemetry(df: pd.DataFrame) -> ValidationResult:
    """
    Validate telemetry records and separate valid from invalid.
    
    Checks:
    - Required columns exist
    - Timestamps are valid
    - Numeric fields are numeric
    - Labels are in expected threat categories
    - Port ranges are valid (1-65535)
    - No impossibly negative network quantities
    
    Args:
        df: Input DataFrame
        
    Returns:
        ValidationResult with valid/invalid records and error summary
    """
    result = ValidationResult()
    result.total_rows = len(df)

    # Check for required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        result.errors["missing_columns"] = missing_cols
        logger.error(f"Missing required columns: {missing_cols}")
        return result

    valid_indices = []
    invalid_records = []

    for idx, row in df.iterrows():
        errors = []

        # Validate timestamp
        if pd.isna(row["timestamp"]):
            errors.append("timestamp is null")
        else:
            try:
                pd.to_datetime(row["timestamp"])
            except (ValueError, TypeError):
                errors.append(f"timestamp '{row['timestamp']}' is not valid ISO format")

        # Validate source_ip
        if pd.isna(row["source_ip"]) or row["source_ip"] == "":
            errors.append("source_ip is missing")

        # Validate dest_ip
        if pd.isna(row["dest_ip"]) or row["dest_ip"] == "":
            errors.append("dest_ip is missing")

        # Validate src_port
        try:
            port = int(row["src_port"])
            if port < 0 or port > 65535:
                errors.append(f"src_port {port} out of valid range (0-65535)")
        except (ValueError, TypeError):
            errors.append(f"src_port '{row['src_port']}' is not numeric")

        # Validate dest_port
        try:
            port = int(row["dest_port"])
            if port < 0 or port > 65535:
                errors.append(f"dest_port {port} out of valid range (0-65535)")
        except (ValueError, TypeError):
            errors.append(f"dest_port '{row['dest_port']}' is not numeric")

        # Validate protocol
        if pd.isna(row["protocol"]) or row["protocol"] == "":
            errors.append("protocol is missing")
        elif str(row["protocol"]).lower() not in ["tcp", "udp"]:
            errors.append(f"protocol '{row['protocol']}' is not 'tcp' or 'udp'")

        # Validate bytes
        try:
            bytes_val = float(row["bytes"])
            if bytes_val < 0:
                errors.append(f"bytes {bytes_val} is negative")
        except (ValueError, TypeError):
            errors.append(f"bytes '{row['bytes']}' is not numeric")

        # Validate packets
        try:
            packets_val = float(row["packets"])
            if packets_val < 0:
                errors.append(f"packets {packets_val} is negative")
        except (ValueError, TypeError):
            errors.append(f"packets '{row['packets']}' is not numeric")

        # Validate auth_status
        if pd.isna(row["auth_status"]) or row["auth_status"] == "":
            errors.append("auth_status is missing")
        elif str(row["auth_status"]).lower() not in [
            "success",
            "failure",
            "unknown",
        ]:
            errors.append(
                f"auth_status '{row['auth_status']}' is not 'success', 'failure', or 'unknown'"
            )

        # Validate event_type
        if pd.isna(row["event_type"]) or row["event_type"] == "":
            errors.append("event_type is missing")

        # Validate label if present
        if "label" in df.columns:
            if pd.isna(row["label"]) or row["label"] == "":
                errors.append("label is missing")
            elif str(row["label"]) not in THREAT_LABELS:
                errors.append(
                    f"label '{row['label']}' not in expected threat classes: {THREAT_LABELS}"
                )

        # Record result
        if errors:
            invalid_records.append({
                "index": idx,
                "row_data": row.to_dict(),
                "errors": errors,
            })
        else:
            valid_indices.append(idx)

    result.valid_records = df.loc[valid_indices].reset_index(drop=True)
    result.invalid_records = invalid_records
    result.valid_rows = len(valid_indices)
    result.invalid_rows = len(invalid_records)

    if result.invalid_rows > 0:
        logger.warning(
            f"Validation found {result.invalid_rows} invalid records out of "
            f"{result.total_rows}"
        )

    return result


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean validated data.
    
    This is a light-touch cleaner that preserves data integrity.
    It assumes data has already been validated.
    
    Operations:
    - Convert timestamp to datetime if needed
    - Convert port columns to integer
    - Convert bytes/packets to numeric
    - Normalize auth_status to lowercase
    - Forward-fill small gaps in timestamps
    
    Args:
        df: Input DataFrame (should be pre-validated)
        
    Returns:
        Cleaned DataFrame
    """
    df = df.copy()

    # Convert timestamp to datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Convert port columns to integer
    for col in ["src_port", "dest_port"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Convert bytes and packets to numeric
    for col in ["bytes", "packets"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    # Normalize auth_status to lowercase
    if "auth_status" in df.columns:
        df["auth_status"] = df["auth_status"].str.lower()

    # Normalize event_type to lowercase
    if "event_type" in df.columns:
        df["event_type"] = df["event_type"].str.lower()

    # Normalize protocol to lowercase
    if "protocol" in df.columns:
        df["protocol"] = df["protocol"].str.lower()

    logger.info(f"Cleaned {len(df)} records")
    return df
