# Financial Risk Intelligence Platform

> End-to-end fraud detection platform for financial transactions: data pipeline,
> feature engineering, anomaly detection, REST API, alerting, and operational
> dashboard.

[![CI](https://github.com/Hotzh3/financial-risk-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Hotzh3/financial-risk-intelligence-platform/actions/workflows/ci.yml)

## Overview

Financial institutions process millions of transactions every day. Detecting
fraudulent or anomalous behavior quickly is critical to reduce losses, protect
customers, and support risk operations.

This project simulates a production-style financial risk intelligence platform
using the IEEE-CIS Fraud Detection dataset. It combines machine learning,
backend APIs, alert persistence, and a dashboard into one portfolio-ready system.

## Current Status

The platform currently includes:

- Data ingestion utilities for IEEE-CIS transaction and identity files.
- Exploratory analysis notebook and generated visual reports.
- Feature engineering pipeline for time, amount, card, and selected V-features.
- Isolation Forest anomaly detection model tracked with MLflow.
- FastAPI application with prediction, transaction metrics, health, and alert endpoints.
- SQLite-backed alert engine with configurable risk threshold.
- Streamlit dashboard for metrics, alert monitoring, and live transaction scoring.
- Unit/integration tests for API health, predictions, alerts, feature engineering, and runtime feature assembly.
- GitHub Actions CI that runs the test suite on push and pull requests.

## System Architecture

```text
Raw IEEE-CIS Data
      |
      v
Data Loading / Cleaning
      |
      v
Feature Engineering
      |
      v
Isolation Forest Model + MLflow Tracking
      |
      +----------------------+----------------------+
      |                      |                      |
      v                      v                      v
FastAPI REST API       Streamlit Dashboard     Alert Engine
/predict               KPIs + Live Scoring     SQLite persistence
/transactions          Alert Panel             Threshold config
/alerts
```

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data Processing | Pandas, Polars | Dataset loading, cleaning, feature preparation |
| Machine Learning | Scikit-learn | Isolation Forest anomaly detection |
| Experiment Tracking | MLflow | Model and metric tracking |
| API | FastAPI, Pydantic | Typed REST API and validation |
| Dashboard | Streamlit | Operational UI for risk monitoring |
| Database | SQLite | Local alert persistence |
| Testing | Pytest | Unit and integration tests |
| Code Quality | Ruff | Linting and formatting target |

## Project Roadmap

### Completed

- [x] Phase 0 — Repository structure and environment setup
- [x] Phase 1 — Initial data exploration and EDA notebook
- [x] Phase 2 — Feature engineering baseline
- [x] Phase 3 — Isolation Forest model training with MLflow
- [x] Phase 4 — FastAPI REST API baseline
- [x] Phase 5 — Streamlit dashboard baseline
- [x] Phase 6 — Alert engine with SQLite persistence
- [x] Phase 7 — Basic API and alert tests
- [x] Phase 8 — CI workflow, import-stable pytest config, and expanded regression tests

### In Progress / Next Improvements

- [ ] Reproducible cleaning pipeline in `src/data/clean_data.py`
- [ ] Remove possible feature leakage from card-based aggregate features
- [ ] Load model and feature order from artifacts instead of hardcoded runtime values
- [ ] Align `requirements.txt` with the active Python environment
- [ ] Replace deprecated Pydantic `Field(example=...)` usage
- [ ] Configure API URL, CORS origins, and alert database path via environment variables
- [ ] Add Docker / docker-compose for reproducible local deployment
- [ ] Plan production database migration from SQLite to PostgreSQL

## Dataset

This project uses the
[IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)
dataset from Kaggle.

The raw dataset is intentionally not committed to Git because of its size.
For the same reason, generated processed data artifacts are also expected to
remain local unless a small synthetic fixture is created specifically for tests.

Expected local structure:

```text
data/
├── raw/
│   ├── train_transaction.csv
│   ├── train_identity.csv
│   ├── test_transaction.csv
│   ├── test_identity.csv
│   └── sample_submission.csv
└── processed/
    └── train_clean.parquet
```

For the Phase 1 pipeline in this repository, place your main training CSV inside
`data/raw/` using one of these names:

- `transactions.csv` (recommended default for this project)
- `creditcard.csv`
- `train_transaction.csv`

The loader in `src/data/load_data.py` will auto-detect one of those files.

## Phase 1 Workflow (Data + EDA)

Current focus is building a reliable data foundation before modeling:

1. Load raw data from `data/raw/`
2. Validate schema and key columns
3. Clean duplicates, data types, and missing values
4. Save clean output to `data/processed/transactions_clean.csv`
5. Analyze distributions and class imbalance in `notebooks/01_eda.ipynb`

Run scripts:

```bash
python -m src.data.load_data
python -m src.data.clean_data
```

Notebook:

```bash
jupyter notebook notebooks/01_eda.ipynb
```

## Getting Started

```bash
# Clone the repository
git clone https://github.com/Hotzh3/financial-risk-intelligence-platform.git
cd financial-risk-intelligence-platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn api.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Running the Dashboard

In a second terminal, with the API running:

```bash
streamlit run dashboard/app.py
```

Dashboard default URL:

```text
http://localhost:8501
```

## Screenshots / Demo

Dedicated screenshot and demo notes live in [`docs/screenshots/`](docs/screenshots/).
Use that folder for portfolio-ready images such as API docs, dashboard overview,
alert monitoring, and prediction examples.

The repository also includes generated analysis visuals under `reports/` that can be
used to document the workflow and model exploration:

- `reports/fraud_distribution.png`
- `reports/amount_analysis.png`
- `reports/temporal_analysis.png`
- `reports/feature_correlations.png`
- `reports/product_card_analysis.png`

Recommended demo flow for a short walkthrough:

1. Start the API with `uvicorn api.main:app --reload`.
2. Open `http://127.0.0.1:8000/docs` to show live prediction and alert routes.
3. Launch `streamlit run dashboard/app.py` to demonstrate dashboard scoring and monitoring.

## Running Tests

Test documentation lives in [`tests/README.md`](tests/README.md).

```bash
pytest -q
```

Current local result for this phase: `15 passed`.

`pytest.ini` configures the repository root on `PYTHONPATH`, so both
`python -m pytest -q` and plain `pytest -q` work from the top-level directory.

The automated CI workflow runs on every push and pull request with Python 3.11,
installs dependencies from `requirements.txt`, and executes the same `pytest -q`
command used locally.

## Project Structure

```text
financial-risk-intelligence-platform/
├── api/                    # FastAPI application and routers
│   ├── main.py
│   ├── routers/
│   │   ├── alerts.py
│   │   ├── predictions.py
│   │   └── transactions.py
│   └── schemas/
├── config/                 # Project configuration
├── dashboard/              # Streamlit dashboard
├── data/                   # Local raw and processed datasets (not for Git)
├── docs/                   # Project documentation
│   └── screenshots/        # Portfolio screenshot/demo capture notes
├── models/                 # Local model artifacts and feature order
├── notebooks/              # Exploratory data analysis
├── reports/                # Generated analysis figures
├── src/                    # Core application and ML code
│   ├── alerts/             # Alert engine and persistence
│   ├── data/               # Data loading and cleaning pipeline
│   ├── features/           # Feature engineering
│   ├── models/             # Training and evaluation
│   └── utils/              # Shared utilities
└── tests/                  # Unit and integration tests
    └── README.md           # Test suite guide
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Service health check |
| POST | `/api/v1/predict` | Score a transaction for fraud risk |
| GET | `/api/v1/transactions` | Transaction history placeholder |
| GET | `/api/v1/metrics` | System and model metrics |
| GET | `/api/v1/alerts` | Recent generated alerts |
| GET | `/api/v1/alerts/stats` | Alert severity and notification statistics |
| PATCH | `/api/v1/alerts/threshold` | Update runtime alert threshold |

## Model Snapshot

The current baseline anomaly detector is an Isolation Forest model. The API
exposes an approximate ROC-AUC of `0.7120`, so it is reasonable to describe the
current model performance as roughly `0.71 ROC-AUC` while the feature set and
threshold calibration continue to evolve.

## Known Limitations

- The current transaction history endpoint is still a placeholder.
- Some metrics are hardcoded and should eventually be loaded from MLflow or a model registry.
- The cleaning pipeline needs to be fully implemented for complete reproducibility.
- Card-based aggregate features should be refactored to avoid train/test leakage.
- Runtime configuration should be moved further into environment variables.
- Local SQLite persistence is appropriate for development, but not for multi-user production workloads.

## Author

**José Gerardo Malfavaun Gorostizaga** — Data Science & Engineering Portfolio

- LinkedIn: https://www.linkedin.com/in/jos%C3%A9-gerardo-malfavaun-gorostizaga/
- GitHub: https://github.com/Hotzh3
