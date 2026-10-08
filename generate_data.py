"""Generate synthetic telemetry data for demonstration and training.

This module creates realistic but completely synthetic cybersecurity telemetry
for local testing without any real network interaction, attacks, or data transfer.
"""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from config import DATA_DIR, DEMO_ATTACKS_CSV, NORMAL_CSV, SAMPLE_TELEMETRY_CSV

logger = logging.getLogger(__name__)

# Set seed for reproducibility
random.seed(42)


def generate_normal_records(count: int = 300) -> list[dict]:
    """
    Generate synthetic normal network traffic records.
    
    Characteristics:
    - Regular business hours activity
    - Common ports (80, 443, 3389, 445)
    - Balanced success/failure auth
    - Moderate data transfer
    - Consistent peer relationships
    
    Args:
        count: Number of normal records to generate
        
    Returns:
        List of telemetry dictionaries
    """
    records = []
    base_time = datetime(2026, 10, 8, 8, 0, 0)
    
    internal_ips = [f"10.0.0.{i}" for i in range(5, 25)]
    external_ips = [f"8.8.8.{i}" for i in range(1, 6)]
    
    for i in range(count):
        event_time = base_time + timedelta(seconds=i * 5)
        source_ip = random.choice(internal_ips)
        dest_ip = random.choice(external_ips + internal_ips)
        
        # Avoid self-connections
        while dest_ip == source_ip:
            dest_ip = random.choice(external_ips + internal_ips)
        
        protocol = random.choice(["tcp", "udp"])
        dest_port = random.choice([80, 443, 3389, 445, 22, 25, 53])
        
        records.append({
            "timestamp": event_time.isoformat(),
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "src_port": random.randint(1024, 65535),
            "dest_port": dest_port,
            "protocol": protocol,
            "bytes": random.randint(100, 5000),
            "packets": random.randint(2, 50),
            "auth_status": random.choice(["success"] * 4 + ["failure"]),  # 80% success
            "event_type": random.choice(["http", "https", "rdp", "smb", "ssh", "dns"]),
            "label": "Normal",
        })
    
    return records


def generate_port_scan_records(count: int = 75) -> list[dict]:
    """
    Generate synthetic port scan attack records.
    
    Characteristics:
    - Single source to single destination
    - Many different ports (reconnaissance)
    - Fast connection rate
    - Low bytes per connection
    - Unknown/failed auth status
    
    Args:
        count: Number of port scan records to generate
        
    Returns:
        List of telemetry dictionaries
    """
    records = []
    start_time = datetime(2026, 10, 8, 10, 0, 0)
    source_ip = "192.168.100.50"  # External scanning source
    dest_ip = "10.0.0.12"  # Internal target
    
    for i in range(count):
        event_time = start_time + timedelta(seconds=i)
        
        records.append({
            "timestamp": event_time.isoformat(),
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "src_port": random.randint(50000, 60000),
            "dest_port": 20 + (i % 256),  # Scan across port range
            "protocol": "tcp",
            "bytes": random.randint(40, 120),  # Minimal payload
            "packets": random.randint(1, 3),  # Few packets per connection
            "auth_status": "unknown",
            "event_type": "scan",
            "label": "Port Scan",
        })
    
    return records


def generate_brute_force_records(count: int = 50) -> list[dict]:
    """
    Generate synthetic brute force authentication attack records.
    
    Characteristics:
    - Single source to single destination (target system)
    - Repeated failed authentication attempts
    - SSH or RDP port (22 or 3389)
    - Rapid-fire connections
    - High failure rate
    
    Args:
        count: Number of brute force records to generate
        
    Returns:
        List of telemetry dictionaries
    """
    records = []
    start_time = datetime(2026, 10, 8, 11, 0, 0)
    source_ip = "203.0.113.15"  # External attacker
    dest_ip = "10.0.0.7"  # Target server
    
    for i in range(count):
        event_time = start_time + timedelta(seconds=i * 1.5)
        dest_port = random.choice([22, 3389])  # SSH or RDP
        
        records.append({
            "timestamp": event_time.isoformat(),
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "src_port": random.randint(40000, 50000),
            "dest_port": dest_port,
            "protocol": "tcp",
            "bytes": random.randint(80, 250),
            "packets": random.randint(3, 8),
            "auth_status": "failure",  # Almost all failures
            "event_type": "login",
            "label": "Brute Force",
        })
    
    return records


def generate_lateral_movement_records(count: int = 65) -> list[dict]:
    """
    Generate synthetic lateral movement attack records.
    
    Characteristics:
    - Source is internal (compromised host)
    - Targets other internal hosts
    - Uses admin/sensitive ports (445 SMB, 3389 RDP)
    - Irregular patterns compared to normal
    - Mix of success/failure auth
    
    Args:
        count: Number of lateral movement records to generate
        
    Returns:
        List of telemetry dictionaries
    """
    records = []
    start_time = datetime(2026, 10, 8, 12, 0, 0)
    source_ip = "10.0.0.18"  # Compromised internal host
    target_ips = [f"10.0.0.{i}" for i in range(1, 15)]  # Other internal targets
    
    for i in range(count):
        event_time = start_time + timedelta(seconds=i * 2)
        dest_ip = random.choice(target_ips)
        
        # Avoid self-connection
        while dest_ip == source_ip:
            dest_ip = random.choice(target_ips)
        
        records.append({
            "timestamp": event_time.isoformat(),
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "src_port": random.randint(49152, 65535),
            "dest_port": random.choice([445, 3389, 135, 139]),  # Admin/sensitive ports
            "protocol": "tcp",
            "bytes": random.randint(200, 1500),
            "packets": random.randint(5, 20),
            "auth_status": random.choice(["success"] * 2 + ["failure"]),  # Mix
            "event_type": random.choice(["smb", "rdp", "wmi"]),
            "label": "Lateral Movement",
        })
    
    return records


def generate_data_exfiltration_records(count: int = 40) -> list[dict]:
    """
    Generate synthetic data exfiltration attack records.
    
    Characteristics:
    - Source is internal (compromised host)
    - Destination is external (attacker-controlled)
    - Very high bytes transferred
    - Sustained high-volume transfer
    - Unusual timing/volume patterns
    
    Args:
        count: Number of data exfiltration records to generate
        
    Returns:
        List of telemetry dictionaries
    """
    records = []
    start_time = datetime(2026, 10, 8, 13, 0, 0)
    source_ip = "10.0.0.22"  # Internal exfiltrating host
    dest_ip = "198.51.100.99"  # External attacker C&C
    
    for i in range(count):
        event_time = start_time + timedelta(minutes=i)
        
        records.append({
            "timestamp": event_time.isoformat(),
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "src_port": random.randint(49152, 65535),
            "dest_port": random.choice([443, 8080, 9999]),  # HTTPS or custom
            "protocol": "tcp",
            "bytes": random.randint(500000, 2000000),  # Very high volume
            "packets": random.randint(300, 800),  # Many packets
            "auth_status": "success",
            "event_type": "transfer",
            "label": "Data Exfiltration",
        })
    
    return records


def generate_malformed_records(count: int = 15) -> list[dict]:
    """
    Generate malformed/noisy records for robustness testing.
    
    These records contain:
    - Missing fields
    - Invalid data types
    - Malformed timestamps
    - Out-of-range values
    
    Args:
        count: Number of malformed records to generate
        
    Returns:
        List of malformed telemetry dictionaries
    """
    records = []
    
    malformed_templates = [
        {  # Missing field
            "timestamp": "2026-10-08T14:00:00Z",
            "source_ip": "10.0.0.5",
            # 'dest_ip' missing
            "src_port": 1234,
            "dest_port": 80,
            "protocol": "tcp",
            "bytes": 100,
            "packets": 2,
            "auth_status": "unknown",
            "event_type": "http",
            "label": "Normal",
        },
        {  # Invalid port number
            "timestamp": "2026-10-08T14:01:00Z",
            "source_ip": "10.0.0.6",
            "dest_ip": "8.8.8.8",
            "src_port": "invalid_port",
            "dest_port": 443,
            "protocol": "tcp",
            "bytes": 200,
            "packets": 3,
            "auth_status": "success",
            "event_type": "https",
            "label": "Normal",
        },
        {  # Malformed timestamp
            "timestamp": "not-a-timestamp",
            "source_ip": "10.0.0.7",
            "dest_ip": "8.8.4.4",
            "src_port": 5555,
            "dest_port": 53,
            "protocol": "udp",
            "bytes": 150,
            "packets": 1,
            "auth_status": "unknown",
            "event_type": "dns",
            "label": "Normal",
        },
        {  # Negative bytes
            "timestamp": "2026-10-08T14:02:00Z",
            "source_ip": "10.0.0.8",
            "dest_ip": "1.1.1.1",
            "src_port": 6666,
            "dest_port": 80,
            "protocol": "tcp",
            "bytes": -500,
            "packets": 2,
            "auth_status": "success",
            "event_type": "http",
            "label": "Normal",
        },
    ]
    
    for i in range(count):
        records.append(malformed_templates[i % len(malformed_templates)])
    
    return records


def generate_all(output_dir: Path | None = None, seed: int | None = None) -> tuple[Path, Path, Path]:
    """
    Generate all synthetic datasets and save to CSV files.
    
    Args:
        output_dir: Directory to save CSV files (defaults to config.DATA_DIR)
        seed: Random seed for reproducibility (defaults to 42)
        
    Returns:
        Tuple of (normal_csv_path, attacks_csv_path, combined_csv_path)
    """
    if seed is not None:
        random.seed(seed)
    
    if output_dir is None:
        output_dir = DATA_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Generating synthetic telemetry data...")
    
    # Generate all record types
    logger.info("  - Normal traffic...")
    normal_records = generate_normal_records(count=300)
    
    logger.info("  - Port scan attacks...")
    port_scan_records = generate_port_scan_records(count=75)
    
    logger.info("  - Brute force attacks...")
    brute_force_records = generate_brute_force_records(count=50)
    
    logger.info("  - Lateral movement...")
    lateral_records = generate_lateral_movement_records(count=65)
    
    logger.info("  - Data exfiltration...")
    exfiltration_records = generate_data_exfiltration_records(count=40)
    
    logger.info("  - Malformed records...")
    malformed_records = generate_malformed_records(count=15)
    
    # Create DataFrames
    df_normal = pd.DataFrame(normal_records)
    df_attacks = pd.DataFrame(
        port_scan_records
        + brute_force_records
        + lateral_records
        + exfiltration_records
        + malformed_records
    )
    df_combined = pd.concat([df_normal, df_attacks], ignore_index=True)
    
    # Sort by timestamp for natural ordering
    df_combined["timestamp_dt"] = pd.to_datetime(
        df_combined["timestamp"], errors="coerce"
    )
    df_combined = df_combined.sort_values("timestamp_dt", na_position="last")
    df_combined = df_combined.drop(columns=["timestamp_dt"])
    df_combined = df_combined.reset_index(drop=True)
    
    # Save to CSV
    normal_csv = output_dir / "normal_traffic.csv"
    attacks_csv = output_dir / "demo_attacks.csv"
    combined_csv = output_dir / "sample_telemetry.csv"
    
    df_normal.to_csv(normal_csv, index=False)
    df_attacks.to_csv(attacks_csv, index=False)
    df_combined.to_csv(combined_csv, index=False)
    
    logger.info(f"\nDatasets created:")
    logger.info(f"  Normal traffic: {normal_csv}")
    logger.info(f"  Attacks demo: {attacks_csv}")
    logger.info(f"  Combined sample: {combined_csv}")
    
    return normal_csv, attacks_csv, combined_csv


def print_dataset_summary(csv_path: Path) -> None:
    """
    Load and print summary statistics of a dataset.
    
    Args:
        csv_path: Path to CSV file
    """
    df = pd.read_csv(csv_path)
    
    print(f"\n{'='*70}")
    print(f"Dataset: {csv_path.name}")
    print(f"{'='*70}")
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\nColumns: {', '.join(df.columns.tolist())}")
    
    if "label" in df.columns:
        print(f"\nLabel Distribution:")
        label_counts = df["label"].value_counts()
        for label, count in label_counts.items():
            pct = (count / len(df)) * 100
            print(f"  {label:25s}: {count:5d} ({pct:5.1f}%)")
    
    print(f"\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print(f"\nData Types:")
    print(df.dtypes)
    print()


if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    
    # Parse command-line arguments
    seed = 42
    if "--seed" in sys.argv:
        idx = sys.argv.index("--seed")
        if idx + 1 < len(sys.argv):
            seed = int(sys.argv[idx + 1])
    
    # Generate datasets
    normal_csv, attacks_csv, combined_csv = generate_all(seed=seed)
    
    # Print summaries
    print_dataset_summary(normal_csv)
    print_dataset_summary(attacks_csv)
    print_dataset_summary(combined_csv)
    
    print("\n✅ Phase 2 complete: Synthetic telemetry generated successfully!")
