"""Central configuration file for Cybersecurity Sentinel."""

from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Data directories
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_DIR = BASE_DIR / "database"

# Database
DB_PATH = DB_DIR / "alerts.db"

# Data files
NORMAL_CSV = DATA_DIR / "normal_traffic.csv"
DEMO_ATTACKS_CSV = DATA_DIR / "demo_attacks.csv"
SAMPLE_TELEMETRY_CSV = DATA_DIR / "sample_telemetry.csv"

# Model files
ANOMCALY_MODEL_PATH = MODELS_DIR / "anomaly_model.pkl"
CLASSIFIER_MODEL_PATH = MODELS_DIR / "classifier.pkl"

# Policy settings
MAX_RISK_DEFAULT = 70

# Threat classifications
THREAT_LABELS = [
    "Normal",
    "Port Scan",
    "Brute Force",
    "Lateral Movement",
    "Data Exfiltration",
]

# Required telemetry columns
REQUIRED_COLUMNS = [
    "timestamp",
    "source_ip",
    "dest_ip",
    "src_port",
    "dest_port",
    "protocol",
    "bytes",
    "packets",
    "auth_status",
    "event_type",
]

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Feature engineering
FEATURE_WINDOW_SIZE = 300  # seconds
MIN_RECORDS_FOR_FEATURES = 5
