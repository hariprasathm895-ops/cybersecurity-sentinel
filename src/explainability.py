"""Generate explanations for alerts."""
from __future__ import annotations
import logging
import pandas as pd
logger = logging.getLogger(__name__)

def generate_evidence(row: pd.Series, threat_type: str) -> dict:
    return {
        "threat_type": str(threat_type),
        "source_ip": row.get("source_ip"),
        "dest_ip": row.get("dest_ip"),
        "anomaly_score": float(row.get("anomaly_score", 0) or 0),
        "auth_failure_rate": float(row.get("auth_failure_rate", 0) or 0),
        "unique_dest_ports": int(row.get("unique_dest_ports", 0) or 0),
        "total_bytes_window": float(row.get("total_bytes_window", 0) or 0),
        "is_scan_pattern": bool(row.get("is_scan_pattern", 0)),
        "is_exfil_pattern": bool(row.get("is_exfil_pattern", 0)),
        "risk_score": float(row.get("risk_score", 0) or 0),
    }

def format_alert_explanation(evidence: dict, threat_type: str) -> str:
    src = evidence.get("source_ip", "unknown")
    dst = evidence.get("dest_ip", "unknown")
    risk = evidence.get("risk_score", 0)
    anomaly = evidence.get("anomaly_score", 0)
    signals = []
    if evidence.get("is_scan_pattern"):
        signals.append(f"scan-like: {evidence.get('unique_dest_ports', 0)} ports accessed")
    if evidence.get("is_exfil_pattern"):
        signals.append(f"exfil-like: {evidence.get('total_bytes_window', 0):.0f} bytes")
    if evidence.get("auth_failure_rate", 0) > 0.3:
        signals.append(f"auth failures: {evidence.get('auth_failure_rate', 0):.1%}")
    if anomaly > 50:
        signals.append(f"anomaly score: {anomaly:.0f}")
    reason = "; ".join(signals) if signals else "behavioral match"
    return f"{threat_type}: {src} -> {dst}. {reason}. Risk={risk:.0f}"
