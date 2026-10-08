# Intelligent Cyber Threat and Network Anomaly Detection

## 1. Project Overview

Cybersecurity Sentinel is a Python-based demo project for detecting suspicious network behavior from synthetic telemetry. It ingests CSV telemetry, validates the data, generates behavioral features, applies anomaly detection and supervised classification, scores the resulting risk, and stores relevant alerts in SQLite for review.

The project is designed for a hackathon-style defensive monitoring workflow. It helps an operator quickly identify abnormal network activity and understand why a record was flagged. The system focuses on a small set of important threat patterns: normal traffic, port scanning, brute-force authentication attempts, lateral movement, and data exfiltration.

## 2. Problem Statement

Modern security operations teams deal with large amounts of telemetry from endpoints, firewalls, authentication services, and network appliances. Distinguishing legitimate activity from malicious behavior is difficult when the event stream is noisy, incomplete, or contains malformed records. A single alert should not be generated without evidence.

This project addresses that challenge by combining validation, feature engineering, anomaly detection, classification, deterministic risk scoring, and explainable alerting in a compact end-to-end pipeline.

## 3. Key Threats Detected

- Normal Traffic: Standard user and device activity with expected patterns.
- Port Scan: High-volume reconnaissance activity that probes many destination ports from a single source.
- Brute Force: Repeated login or authentication failures against a target service.
- Lateral Movement: Activity from an internal host that moves across internal systems and privileged ports.
- Data Exfiltration: Unusually large outbound transfer patterns suggesting sensitive data leaving the environment.

## 4. Key Features

The project currently implements the following features:

- Telemetry ingestion from CSV files
- Input validation for required columns, timestamp validity, port/binary/numeric checks, and malformed rows
- Behavioral and sliding-window feature generation from telemetry
- Unsupervised anomaly detection using Isolation Forest
- Supervised multiclass threat classification using Random Forest
- Deterministic 0–100 risk scoring
- Risk bands: 0–30 Normal, 31–70 Suspicious, 71–100 Malicious
- Explainable alert generation based on observed feature values
- SQLite audit and alert storage
- Streamlit operator dashboard
- Maximum-risk policy with non-zero exit behavior on threshold breach
- Graceful handling of noisy, malformed, missing, or unknown telemetry

## 5. System Architecture

```text
Telemetry
   ↓
Ingestion & Validation
   ↓
Behavioral Feature Engineering
   ↓
Isolation Forest
   ↓
Random Forest
   ↓
Risk Engine
   ↓
Explainability
   ↓
SQLite
   ↓
Streamlit Dashboard
```

## 6. Technology Stack

The project uses the following technologies:

- Python
- pandas
- NumPy
- scikit-learn
- SQLite
- Streamlit
- Plotly
- pytest
- joblib

## 7. Project Structure

```text
cybersecurity-sentinel/
├── app.py                     # Streamlit dashboard
├── config.py                  # Central project configuration
├── generate_data.py           # Synthetic telemetry generation
├── train_models.py            # Model training entry point
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── test_run.py                # Local validation helper script
├── data/                      # Synthetic telemetry CSV files
│   ├── normal_traffic.csv
│   ├── demo_attacks.csv
│   └── sample_telemetry.csv
├── models/                    # Trained model artifacts (.pkl)
├── database/                  # SQLite database output directory
│   └── alerts.db
├── src/                       # Core analysis modules
│   ├── ingestion.py           # Telemetry loading helpers
│   ├── validation.py          # Data validation and cleaning
│   ├── features.py            # Behavioral feature engineering
│   ├── anomaly_detection.py  # Isolation Forest implementation
│   ├── classification.py      # Random Forest classification
│   ├── risk_engine.py         # Risk scoring logic
│   ├── explainability.py      # Explanation generation
│   ├── database.py            # SQLite operations
│   └── pipeline.py            # End-to-end orchestration
├── tests/                     # Automated tests
│   ├── test_validation.py
│   ├── test_features.py
│   ├── test_risk.py
│   └── test_pipeline.py
└── .venv/                     # Local virtual environment (created by user)
```

## 8. Machine Learning Approach

### Anomaly Detection

The anomaly detection stage uses scikit-learn's Isolation Forest. The project trains a model on normal behavioral telemetry and then scores new records for unusual activity. The model output is converted into an anomaly score used by the risk engine.

### Classification

The classification stage uses scikit-learn's Random Forest classifier to predict one of the following classes:

- Normal
- Port Scan
- Brute Force
- Lateral Movement
- Data Exfiltration

The model is trained on labeled synthetic telemetry and saved under the models directory for reuse during inference.

### Risk Scoring

The risk engine computes a deterministic 0–100 risk score for each record. The current implementation uses a baseline score based on the predicted threat type and then adjusts the result using observed signals such as anomaly score, authentication failure activity, scan indicators, exfiltration patterns, and network behavior. The risk bands are:

- 0–30: Normal
- 31–70: Suspicious
- 71–100: Malicious

## 9. Data Flow

A telemetry record flows through the system in the following sequence:

1. A CSV file is loaded from disk.
2. Required fields are validated and malformed rows are rejected or cleaned safely.
3. Behavioral and sliding-window features are generated for each record.
4. The Isolation Forest model assesses whether the record is anomalous.
5. The Random Forest model predicts the threat class.
6. The risk engine computes a deterministic 0–100 score and assigns a Normal/Suspicious/Malicious label.
7. The explanation engine creates an evidence-based summary from the observed values.
8. The alert is inserted into SQLite for audit and review.
9. The Streamlit dashboard queries stored alerts and displays the results to the operator.

## 10. Installation

Use the following exact Windows commands from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 11. Generate Demo Data

The project uses synthetic, local-only telemetry for demonstration and testing.

```powershell
python generate_data.py --seed 42
```

This command creates demo datasets in the data directory and is intended for local use only.

## 12. Train Models

```powershell
python train_models.py
```

This trains and saves the anomaly detection and classification models into the models directory. The code relies on the generated synthetic datasets and the existing project configuration.

## 13. Run the Detection Pipeline

```powershell
python -m src.pipeline --input data\sample_telemetry.csv --max-risk 70
```

This command loads telemetry, validates it, generates features, runs both ML models, calculates risk, creates explanations, stores alerts in SQLite, and exits with a non-zero status when any alert exceeds the configured maximum-risk threshold.

## 14. Run the Dashboard

```powershell
streamlit run app.py
```

The dashboard provides a basic operator view of recent alerts, threat distribution, risk distribution, alert detail, and SQLite-backed audit information.

## 15. Run Tests

```powershell
python -m pytest -q
```

Tests should be run locally with the command above.

## 16. Maximum-Risk Policy

The project includes a maximum-risk guardrail parameter:

- `--max-risk` sets the allowed risk threshold
- When an alert exceeds the threshold, the pipeline reports the violation and exits with a non-zero process exit code
- The alert is still stored in SQLite for audit purposes

This behavior is implemented in the pipeline and risk evaluation logic.

## 17. Security & Safety

- The telemetry used by this project is synthetic and local-only.
- The project is intended for defensive monitoring and educational demonstration.
- No real systems should be attacked, scanned, or exploited as part of this work.
- Input telemetry is validated before processing to reduce the risk of malformed or unsafe data affecting the pipeline.

## 18. Limitations

The current project is a focused hackathon MVP and has several limitations:

- It relies on synthetic telemetry rather than live production data.
- The feature set is intentionally lean and demonstration-oriented.
- Model evaluation is limited to the available labeled synthetic data.
- Runtime verification status should be confirmed locally before claiming full production readiness.
- The dashboard is a lightweight operational view rather than a full enterprise SOC interface.

## 19. Future Improvements

The following are reasonable future improvements, not current features:

- Richer telemetry sources and real-world data integration
- Better model tuning and validation on larger labeled datasets
- Streaming or near-real-time processing
- Additional feature engineering for host and authentication context
- Improved alert prioritization and triage workflows
- Stronger dashboard role-based access and search/filter capabilities
- More advanced explainability and model comparison tooling

## 20. Hackathon Demo Flow

A simple demonstration sequence for judges and reviewers:

1. Generate synthetic telemetry
2. Train the models
3. Run the detection pipeline
4. Review risk scores and explanations
5. Inspect SQLite alert records
6. Open the Streamlit dashboard
7. Demonstrate the maximum-risk policy behavior

## 21. License / Project Information

This project is a hackathon demonstration repository for the RAALE #11 event. It is intended for local educational and demonstration use.

No formal production license is asserted here unless one is added separately in the repository.

---

Project: Cybersecurity Sentinel  
Theme: Intelligent Cyber Threat and Network Anomaly Detection  
Hackathon: IT HAPPENS @ RAALE #11
