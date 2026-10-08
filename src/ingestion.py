"""Module for ingesting and loading telemetry data from CSV/JSON sources."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_telemetry(file_path: str | Path) -> pd.DataFrame:
    """
    Load telemetry data from CSV or JSON file.
    
    Handles:
    - Missing files with clear error message
    - Empty CSV files
    - Extra/unexpected columns (preserved)
    - Returns DataFrame with all columns intact
    
    Args:
        file_path: Path to telemetry file (CSV or JSON)
        
    Returns:
        DataFrame containing telemetry records
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If file is empty or unreadable
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Telemetry file not found: {file_path}")
    
    if file_path.stat().st_size == 0:
        raise ValueError(f"Telemetry file is empty: {file_path}")
    
    try:
        if file_path.suffix.lower() == ".json":
            df = pd.read_json(file_path, lines=True)
        else:  # Default to CSV
            df = pd.read_csv(file_path)
        
        if df.empty:
            raise ValueError(f"Telemetry file contains no records: {file_path}")
        
        logger.info(f"Loaded {len(df)} records from {file_path.name}")
        return df
    
    except Exception as e:
        raise ValueError(f"Failed to load telemetry from {file_path}: {str(e)}") from e


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to lowercase and handle common variations.
    
    This helps handle different naming conventions:
    - "Source IP" -> "source_ip"
    - "SourceIP" -> "source_ip"
    - "source_ip" -> "source_ip" (no change)
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with normalized column names
    """
    # Convert to lowercase and replace spaces with underscores
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("-", "_")
    
    logger.debug(f"Normalized columns: {df.columns.tolist()}")
    return df
