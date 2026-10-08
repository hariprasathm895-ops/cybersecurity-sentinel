"""SQLite alert storage."""
from __future__ import annotations
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DB_PATH
logger = logging.getLogger(__name__)

def initialize_database(db_path: Path | str | None = None) -> None:
    db_path = Path(db_path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_ip TEXT,
            dest_ip TEXT,
            threat_type TEXT,
            risk_score REAL,
            risk_level TEXT,
            anomaly_score REAL,
            explanation TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def insert_alert(alert_record: dict, db_path: Path | str | None = None) -> int:
    db_path = Path(db_path or DB_PATH)
    initialize_database(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "INSERT INTO alerts (timestamp, source_ip, dest_ip, threat_type, risk_score, risk_level, anomaly_score, explanation, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            alert_record.get("timestamp", ""),
            alert_record.get("source_ip", ""),
            alert_record.get("dest_ip", ""),
            alert_record.get("threat_type", ""),
            float(alert_record.get("risk_score", 0) or 0),
            alert_record.get("risk_level", ""),
            float(alert_record.get("anomaly_score", 0) or 0),
            alert_record.get("explanation", ""),
            alert_record.get("status", "new"),
        ),
    )
    conn.commit()
    rid = cursor.lastrowid
    conn.close()
    return rid

def get_alerts(limit: int = 100, db_path: Path | str | None = None) -> list[dict]:
    db_path = Path(db_path or DB_PATH)
    if not db_path.exists():
        return []
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_statistics(db_path: Path | str | None = None) -> dict:
    db_path = Path(db_path or DB_PATH)
    if not db_path.exists():
        return {"total": 0, "by_threat": {}, "by_level": {}}
    conn = sqlite3.connect(db_path)
    total = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    by_threat = conn.execute("SELECT threat_type, COUNT(*) as c FROM alerts GROUP BY threat_type").fetchall()
    by_level = conn.execute("SELECT risk_level, COUNT(*) as c FROM alerts GROUP BY risk_level").fetchall()
    conn.close()
    return {"total": total, "by_threat": dict(by_threat), "by_level": dict(by_level)}
