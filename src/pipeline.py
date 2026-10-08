"""Complete end-to-end pipeline."""
from __future__ import annotations
import argparse
import logging
from pathlib import Path
from config import ANOMCALY_MODEL_PATH, CLASSIFIER_MODEL_PATH, DB_PATH, FEATURE_WINDOW_SIZE, MAX_RISK_DEFAULT
from src.ingestion import load_telemetry, normalize_columns
from src.validation import validate_telemetry, clean_data
from src.features import generate_features
from src.anomaly_detection import detect_anomalies, train_anomaly_detector
from src.classification import classify_threats, train_classifier
from src.risk_engine import calculate_risk_score, evaluate_policy
from src.explainability import generate_evidence, format_alert_explanation
from src.database import initialize_database, insert_alert
logger = logging.getLogger(__name__)

def run_pipeline(input_file: str, max_risk: int = MAX_RISK_DEFAULT) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    input_path = Path(input_file)
    if not input_path.exists():
        logger.error(f"File not found: {input_path}")
        return 1
    logger.info(f"Loading {input_path}")
    df = load_telemetry(input_path)
    df = normalize_columns(df)
    logger.info(f"Validating {len(df)} records")
    val = validate_telemetry(df)
    if val.invalid_rows > 0:
        logger.warning(f"Dropped {val.invalid_rows} bad records")
    df = val.valid_records
    if df.empty:
        logger.error("No valid records")
        return 1
    df = clean_data(df)
    logger.info(f"Generating features for {len(df)} records")
    df = generate_features(df, window_size=FEATURE_WINDOW_SIZE)
    if "label" in df.columns and df["label"].notna().any():
        logger.info("Training classifier")
        try:
            train_classifier(df, CLASSIFIER_MODEL_PATH)
        except Exception as e:
            logger.warning(f"Classifier training failed: {e}")
    normal_subset = df[df.get("label", "Normal").astype(str).str.lower() == "normal"] if "label" in df.columns else df.head(100)
    if len(normal_subset) > 0:
        logger.info("Training anomaly detector")
        train_anomaly_detector(normal_subset, ANOMCALY_MODEL_PATH)
    logger.info("Running anomaly detection")
    df = detect_anomalies(df, ANOMCALY_MODEL_PATH)
    logger.info("Running classification")
    df = classify_threats(df, CLASSIFIER_MODEL_PATH)
    if "predicted_threat" not in df.columns:
        df["predicted_threat"] = df.get("label", "Normal")
    logger.info("Calculating risk scores")
    df = calculate_risk_score(df, max_risk=max_risk)
    logger.info("Storing alerts")
    initialize_database(DB_PATH)
    for _, row in df.iterrows():
        threat = str(row.get("predicted_threat", "Normal"))
        evidence = generate_evidence(row, threat)
        explanation = format_alert_explanation(evidence, threat)
        ts = str(row.get("timestamp", ""))
        alert = {"timestamp": ts, "source_ip": row.get("source_ip"), "dest_ip": row.get("dest_ip"), "threat_type": threat, "risk_score": row.get("risk_score", 0), "risk_level": row.get("risk_level", "Normal"), "anomaly_score": row.get("anomaly_score", 0), "explanation": explanation}
        insert_alert(alert, DB_PATH)
    policy = evaluate_policy(df["risk_score"].tolist(), max_risk)
    logger.info(f"Policy: {policy}")
    high = len(df[df["risk_score"] > max_risk])
    if high > 0:
        logger.warning(f"{high} alerts exceeded max-risk {max_risk}")
        return 1
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/sample_telemetry.csv")
    parser.add_argument("--max-risk", type=int, default=MAX_RISK_DEFAULT)
    args = parser.parse_args()
    raise SystemExit(run_pipeline(args.input, args.max_risk))
