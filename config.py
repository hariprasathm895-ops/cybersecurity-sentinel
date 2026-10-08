from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
DB_DIR = BASE_DIR / "database"
DB_PATH = DB_DIR / "alerts.db"
NORMAL_CSV = DATA_DIR / "normal_traffic.csv"
DEMO_ATTACKS_CSV = DATA_DIR / "demo_attacks.csv"
SAMPLE_TELEMETRY_CSV = DATA_DIR / "sample_telemetry.csv"
MAX_RISK_DEFAULT = 70
THREAT_LABELS = [
    "Normal",
    "Port Scan",
    "Brute Force",
    "Lateral Movement",
    "Data Exfiltration",
]

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
