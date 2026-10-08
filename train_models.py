"""Train models from synthetic data."""
from __future__ import annotations
import logging
from pathlib import Path
from config import DATA_DIR
from generate_data import generate_all
from src.ingestion import load_telemetry, normalize_columns
from src.validation import validate_telemetry, clean_data
from src.features import generate_features
from src.anomaly_detection import train_anomaly_detector
from src.classification import train_classifier
logger = logging.getLogger(__name__)

def train_all_models() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    normal_csv = DATA_DIR / "normal_traffic.csv"
    attacks_csv = DATA_DIR / "demo_attacks.csv"
    if not normal_csv.exists() or not attacks_csv.exists():
        logger.info("Generating synthetic data")
        generate_all()
    logger.info("Training anomaly detector on normal traffic")
    normal_df = load_telemetry(normal_csv)
    normal_df = normalize_columns(normal_df)
    normal_df = validate_telemetry(normal_df).valid_records
    normal_df = clean_data(normal_df)
    normal_df = generate_features(normal_df)
    train_anomaly_detector(normal_df)
    logger.info("Training classifier on attack data")
    attack_df = load_telemetry(attacks_csv)
    attack_df = normalize_columns(attack_df)
    attack_df = validate_telemetry(attack_df).valid_records
    attack_df = clean_data(attack_df)
    attack_df = generate_features(attack_df)
    train_classifier(attack_df)
    logger.info("Done")

if __name__ == "__main__":
    train_all_models()
