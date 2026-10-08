"""Streamlit dashboard."""
from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from config import DB_PATH
from src.database import get_alerts, get_statistics, initialize_database
logger = logging.getLogger(__name__)

def main() -> None:
    initialize_database(DB_PATH)
    st.set_page_config(page_title="Cybersecurity Sentinel", layout="wide")
    st.title("🛡️ Cybersecurity Sentinel")
    st.caption("Intelligent Cyber Threat and Network Anomaly Detection")
    alerts = get_alerts(limit=500, db_path=DB_PATH)
    if not alerts:
        st.warning("No alerts yet. Run the pipeline first.")
        return
    df = pd.DataFrame(alerts)
    for col in ["risk_score", "anomaly_score"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    stats = get_statistics(db_path=DB_PATH)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total alerts", stats.get("total", 0))
    col2.metric("Malicious", stats.get("by_level", {}).get("Malicious", 0))
    col3.metric("Suspicious", stats.get("by_level", {}).get("Suspicious", 0))
    col4.metric("Normal", stats.get("by_level", {}).get("Normal", 0))
    threat_data = stats.get("by_threat", {})
    if threat_data:
        fig = px.bar(x=list(threat_data.keys()), y=list(threat_data.values()), title="Alerts by Threat Type", labels={"x": "Threat", "y": "Count"})
        st.plotly_chart(fig, use_container_width=True)
    fig = px.histogram(df, x="risk_score", nbins=20, title="Risk Score Distribution", color_discrete_sequence=["#dc2626"])
    st.plotly_chart(fig, use_container_width=True)
    st.subheader("Recent Alerts")
    display_cols = [c for c in ["id", "timestamp", "source_ip", "dest_ip", "threat_type", "risk_score", "risk_level"] if c in df.columns]
    st.dataframe(df[display_cols].head(50), use_container_width=True)
    if "id" in df.columns and len(df) > 0:
        st.subheader("Alert Detail")
        sel_id = st.selectbox("Select alert", options=df["id"].tolist())
        sel = df[df["id"] == sel_id].iloc[0]
        st.write(f"**Threat:** {sel.get('threat_type')}")
        st.write(f"**Risk:** {sel.get('risk_score')} ({sel.get('risk_level')})")
        st.write(f"**Source:** {sel.get('source_ip')} → **Dest:** {sel.get('dest_ip')}")
        st.text(sel.get("explanation", "No explanation"))

if __name__ == "__main__":
    main()
