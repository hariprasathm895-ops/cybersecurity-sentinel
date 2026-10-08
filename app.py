import argparse
import json
import os
from pathlib import Path

from config import DATA_DIR, DEMO_ATTACKS_CSV, MAX_RISK_DEFAULT, NORMAL_CSV, SAMPLE_TELEMETRY_CSV


def build_dataset_files() -> None:
    """Generate demo CSV files using the synthetic generator."""
    import generate_data

    generate_data.generate_all()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cybersecurity Sentinel pipeline")
    parser.add_argument("--input", type=str, default=str(SAMPLE_TELEMETRY_CSV), help="Path to telemetry CSV file")
    parser.add_argument("--max-risk", type=int, default=MAX_RISK_DEFAULT, help="Maximum allowed risk threshold")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    from src.pipeline import run_pipeline

    return run_pipeline(args.input, args.max_risk)


if __name__ == "__main__":
    raise SystemExit(main())
