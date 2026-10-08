# 🛡️ Cybersecurity Sentinel

Intelligent Cyber Threat and Network Anomaly Detection System

**IT HAPPENS @ RAALE #11 Hackathon**

## Quick Start (Windows)

```powershell
cd path\to\cybersecurity-sentinel

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Generate synthetic telemetry
python generate_data.py --seed 42

# Train ML models
python train_models.py

# Run the pipeline
python -m src.pipeline --input data\sample_telemetry.csv --max-risk 70

# Start the Streamlit dashboard
streamlit run app.py

# Run tests
pytest -q
```

## Pipeline Stages

1. **Ingestion** — Load telemetry CSV files
2. **Validation** — Check for malformed/missing data
3. **Features** — Generate behavioral/sliding-window features
4. **Anomaly Detection** — Isolation Forest model
5. **Classification** — Random Forest multiclass (5 threat types)
6. **Risk Scoring** — Deterministic 0–100 risk scale
7. **Explanation** — Evidence-based alert reasoning
8. **Storage** — SQLite alert database
9. **Dashboard** — Streamlit operator interface
10. **Policy** — Configurable maximum-risk guardrail

## Threat Classes

- **Normal** — Legitimate activity
- **Port Scan** — Reconnaissance
- **Brute Force** — Authentication attack
- **Lateral Movement** — Internal privilege escalation
- **Data Exfiltration** — Unauthorized data transfer

## Risk Levels

- **0–30** 🟢 Normal
- **31–70** 🟡 Suspicious
- **71–100** 🔴 Malicious

## Example Commands

```powershell
# Run with default settings (max-risk=70)
python -m src.pipeline --input data\sample_telemetry.csv

# Run with custom max-risk threshold
python -m src.pipeline --input data\sample_telemetry.csv --max-risk 60

# Run tests
pytest tests/ -q
```

## Architecture

- **Language** — Python 3.9+
- **ML** — scikit-learn (Isolation Forest, Random Forest)
- **Data** — pandas, NumPy
- **UI** — Streamlit, Plotly
- **Storage** — SQLite3 (Python built-in)
- **Modeling** — joblib
- **Testing** — pytest

## Notes

- All data is **synthetic and local-only**.
- No real attacks, scanning, or data exfiltration.
- Models are trained and cached automatically.
- Exit code 0 = policy passed; non-zero = policy breached.

## Project Structure

```
cybersecurity-sentinel/
├── app.py                    # Streamlit dashboard
├── generate_data.py          # Synthetic data generator
├── train_models.py           # Model training
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── README.md                 # This file
│
├── src/
│   ├── ingestion.py          # CSV loading
│   ├── validation.py         # Data validation
│   ├── features.py           # Feature engineering
│   ├── anomaly_detection.py  # Isolation Forest
│   ├── classification.py     # Random Forest
│   ├── risk_engine.py        # Risk scoring
│   ├── explainability.py     # Alert explanations
│   ├── database.py           # SQLite operations
│   └── pipeline.py           # Orchestration
│
├── data/                     # Telemetry CSVs
├── models/                   # Trained models (.pkl)
├── database/                 # alerts.db
│
└── tests/                    # Test suite
    ├── test_validation.py
    ├── test_features.py
    ├── test_risk.py
    └── test_pipeline.py
```

## Authors

Cybersecurity Sentinel Team — IT HAPPENS @ RAALE #11 Hackathon
