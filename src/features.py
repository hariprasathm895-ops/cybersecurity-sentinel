"""Module for generating behavioral and sliding-window features from telemetry."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def generate_features(df: pd.DataFrame, window_size: int = 300) -> pd.DataFrame:
    """
    Generate behavioral and sliding-window features.
    
    Creates temporal and statistical features for anomaly detection:
    - Unique destination IPs per source
    - Unique ports accessed per source
    - Bytes transferred per source
    - Packet rate per source
    - Connection rate
    - Authentication failure rate
    - Protocol distribution
    
    Args:
        df: Input telemetry DataFrame (must have timestamp in datetime format)
        window_size: Time window in seconds for aggregation
        
    Returns:
        DataFrame with original data + engineered features
    """
    df = df.copy()

    if 'timestamp' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    df = df.sort_values('timestamp', na_position='last').reset_index(drop=True)

    logger.info(f"Generating features with window_size={window_size}s...")

    df['unique_dest_ips'] = 0
    df['unique_dest_ports'] = 0
    df['total_bytes_window'] = 0
    df['total_packets_window'] = 0
    df['connection_rate'] = 0.0
    df['auth_failure_rate'] = 0.0
    df['bytes_per_packet_ratio'] = 0.0
    df['port_diversity'] = 0.0
    df['is_scan_pattern'] = 0
    df['is_exfil_pattern'] = 0

    for src_ip in df['source_ip'].dropna().unique():
        mask = df['source_ip'] == src_ip
        src_indices = df[mask].index.tolist()

        for i in src_indices:
            current_time = df.loc[i, 'timestamp']
            if pd.isna(current_time):
                continue

            window_mask = (
                (df['source_ip'] == src_ip)
                & (df['timestamp'] >= current_time - pd.Timedelta(seconds=window_size))
                & (df['timestamp'] <= current_time)
            )
            window_data = df[window_mask]

            if window_data.empty:
                continue

            df.loc[i, 'unique_dest_ips'] = window_data['dest_ip'].nunique()
            df.loc[i, 'unique_dest_ports'] = window_data['dest_port'].nunique()
            df.loc[i, 'total_bytes_window'] = window_data['bytes'].sum()
            df.loc[i, 'total_packets_window'] = window_data['packets'].sum()

            time_range = (window_data['timestamp'].max() - window_data['timestamp'].min()).total_seconds()
            df.loc[i, 'connection_rate'] = len(window_data) / (time_range + 1) if time_range > 0 else 0.0

            total_auth = len(window_data[window_data['auth_status'].notna()])
            if total_auth > 0:
                failures = len(window_data[window_data['auth_status'].str.lower() == 'failure'])
                df.loc[i, 'auth_failure_rate'] = failures / total_auth
            else:
                df.loc[i, 'auth_failure_rate'] = 0.0

            total_packets = window_data['packets'].sum()
            df.loc[i, 'bytes_per_packet_ratio'] = (
                window_data['bytes'].sum() / total_packets if total_packets > 0 else 0.0
            )

            port_dist = window_data['dest_port'].value_counts()
            if len(port_dist) > 1:
                probs = port_dist.values / port_dist.sum()
                df.loc[i, 'port_diversity'] = -np.sum(probs * np.log2(probs + 1e-10))
            else:
                df.loc[i, 'port_diversity'] = 0.0

            if df.loc[i, 'unique_dest_ports'] > 10 and df.loc[i, 'bytes_per_packet_ratio'] < 200:
                df.loc[i, 'is_scan_pattern'] = 1

            if df.loc[i, 'total_bytes_window'] > 1000000 and df.loc[i, 'unique_dest_ips'] < 3:
                df.loc[i, 'is_exfil_pattern'] = 1

    for col in [
        'unique_dest_ips', 'unique_dest_ports', 'total_bytes_window',
        'total_packets_window', 'connection_rate', 'auth_failure_rate',
        'bytes_per_packet_ratio', 'port_diversity', 'is_scan_pattern', 'is_exfil_pattern'
    ]:
        df[col] = df[col].fillna(0)

    logger.info(f"Generated features for {len(df)} records")
    return df


def compute_source_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute statistics grouped by source IP.
    
    Args:
        df: Input telemetry DataFrame
        
    Returns:
        DataFrame with source IP statistics
    """
    stats = []

    for src_ip in df['source_ip'].dropna().unique():
        src_data = df[df['source_ip'] == src_ip]
        auth_failure_pct = 0.0
        if len(src_data) > 0:
            auth_failure_pct = (src_data['auth_status'].str.lower() == 'failure').sum() / len(src_data) * 100

        stats.append({
            'source_ip': src_ip,
            'record_count': len(src_data),
            'unique_dest_ips': src_data['dest_ip'].nunique(),
            'unique_dest_ports': src_data['dest_port'].nunique(),
            'total_bytes': src_data['bytes'].sum(),
            'avg_bytes': src_data['bytes'].mean(),
            'total_packets': src_data['packets'].sum(),
            'avg_packets': src_data['packets'].mean(),
            'auth_failure_pct': auth_failure_pct,
            'unique_event_types': src_data['event_type'].nunique(),
            'time_span_seconds': (
                (src_data['timestamp'].max() - src_data['timestamp'].min()).total_seconds()
                if 'timestamp' in src_data.columns and src_data['timestamp'].notna().any() else 0
            ),
        })

    stats_df = pd.DataFrame(stats)
    logger.info(f"Computed statistics for {len(stats_df)} unique sources")
    return stats_df
