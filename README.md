# 🛡️ Cybersecurity Sentinel

Intelligent Cyber Threat and Network Anomaly Detection System

**IT HAPPENS @ RAALE #11 Hackathon**

## Project Status

🚀 **PHASE 1: Project Structure** - COMPLETE

- [x] Folder structure created
- [x] Configuration file
- [x] Module stubs with docstrings
- [ ] Data generation (Phase 2)
- [ ] Ingestion & validation (Phase 3)
- [ ] Feature engineering (Phase 4)
- [ ] Anomaly detection (Phase 5)
- [ ] Threat classification (Phase 6)
- [ ] Risk scoring (Phase 7)
- [ ] Explainability (Phase 8)
- [ ] Database (Phase 9)
- [ ] Dashboard (Phase 10)
- [ ] Pipeline (Phase 11)
- [ ] Tests (Phase 12)

## Project Structure

```
cybersecurity-sentinel/
├── app.py                          # Streamlit dashboard
├── config.py                       # Central configuration
├── generate_data.py                # Synthetic data generator
├── train_models.py                 # Model training script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
│
├── data/                           # Telemetry data
│   ├── normal_traffic.csv
│   ├── demo_attacks.csv
│   └── sample_telemetry.csv
│
├── models/                         # Trained ML models
│   ├── anomaly_model.pkl
│   └── classifier.pkl
│
├── database/                       # SQLite database
│   └── alerts.db
│
├── src/                            # Core modules
│   ├── __init__.py
│   ├── ingestion.py               # Load telemetry data
│   ├── validation.py              # Validate & clean data
│   ├── features.py                # Generate features
│   ├── anomaly_detection.py       # Unsupervised detection
│   ├── classification.py          # Supervised classification
│   ├── risk_engine.py             # Risk scoring
│   ├── explainability.py          # Alert explanations
│   ├── database.py                # SQLite operations
│   └── pipeline.py                # Main orchestration
│
└── tests/                          # Test suite
    ├── __init__.py
    ├── test_validation.py
    ├── test_features.py
    ├── test_risk.py
    └── test_pipeline.py
```

## Technology Stack

- **Language**: Python 3.11+
- **ML/Data**: Pandas, NumPy, Scikit-learn
- **Web UI**: Streamlit, Plotly
- **Database**: SQLite
- **Model Storage**: Joblib
- **Testing**: Pytest

## Installation

```bash
# Clone repository
git clone https://github.com/hariprasathm895-ops/cybersecurity-sentinel.git
cd cybersecurity-sentinel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start (Coming Next)

1. **Generate synthetic data**:
   ```bash
   python generate_data.py
   ```

2. **Train models**:
   ```bash
   python train_models.py
   ```

3. **Run pipeline**:
   ```bash
   python -m src.pipeline --input data/demo_attacks.csv --max-risk 70
   ```

4. **View dashboard**:
   ```bash
   streamlit run app.py
   ```

## Features (Planned)

✅ Accepts network telemetry from CSV/JSON files  
✅ Validates and cleans input data  
✅ Generates behavioral/sliding-window features  
✅ Detects anomalies using Isolation Forest  
✅ Classifies threats using Random Forest  
✅ Calculates deterministic 0-100 risk scores  
✅ Explains alert generation with evidence  
✅ Stores alerts in SQLite database  
✅ Displays results in Streamlit dashboard  
✅ Configurable maximum-risk policy  
✅ Handles malformed records robustly  
✅ Provides synthetic demo data  

## Threat Types

- **Normal**: Legitimate network activity
- **Port Scan**: Reconnaissance attack (many destinations)
- **Brute Force**: Authentication attack (repeated failures)
- **Lateral Movement**: Internal privilege escalation
- **Data Exfiltration**: Unauthorized data transfer

## Risk Scoring

- **0-30**: 🟢 Normal
- **31-70**: 🟡 Suspicious
- **71-100**: 🔴 Malicious

## Development Roadmap

- Phase 1: ✅ Project structure
- Phase 2: Synthetic data generation
- Phase 3: Data ingestion & validation
- Phase 4: Feature engineering
- Phase 5: Anomaly detection model
- Phase 6: Classification model
- Phase 7: Risk scoring engine
- Phase 8: Explainability system
- Phase 9: SQLite database
- Phase 10: Streamlit dashboard
- Phase 11: CLI pipeline
- Phase 12: Test suite
- Phase 13: Documentation & polish

## Testing

```bash
pytest tests/
```

## Contributing

This is a hackathon project. Code contributions welcome!

## License

MIT License - See LICENSE file for details

## Authors

- Cybersecurity Sentinel Team
- IT HAPPENS @ RAALE #11 Hackathon Participants
