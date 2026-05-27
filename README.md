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

## Phase 2 Workflow (Feature Engineering + Baseline Model)

This phase builds reproducible model-ready features, trains a baseline fraud model,
and evaluates performance using fraud-focused metrics.

Run scripts in order:

```bash
python3 -m src.features.build_features
python3 -m src.models.train
```

Key outputs:

- Feature table: `data/processed/features.csv`
- Trained model: `artifacts/models/fraud_model.pkl`
- Optional anomaly model: `artifacts/models/isolation_forest.pkl`
- Metrics report: `reports/model_metrics.json`

Use the prediction module for inference on new rows:

```bash
python3 -m src.models.predict
```

## Phase 2.5 Workflow (Model Quality Hardening)

Hardening adds reproducible preprocessing and stronger artifact consistency:

- Train-time preprocessing is handled with `sklearn` `Pipeline` + `ColumnTransformer`
- Numeric features are imputed and scaled (`StandardScaler`) before Logistic Regression
- Categorical features are imputed and one-hot encoded with `handle_unknown=ignore`
- Anti-leakage exclusions are applied in feature build (`TransactionID`, target, configured drops)

For faster local iteration on large IEEE-CIS runs, set `modeling.sample_size` in `config/config.yaml` (for example `100000`). The trainer stratifies by the fraud label so the positive rate matches the full feature table before train/test split. Use `null` for full-data training. Logs and `reports/model_metrics.json` record `training_data_mode` (`full` vs `sampled`) and related fields.

Split strategy is config-driven:

- `modeling.split_strategy: "stratified_random"` (default, class-stratified split)
- `modeling.split_strategy: "temporal"` (orders by `TransactionDT` and splits by `modeling.temporal_split.train_quantile`)

Operational threshold analysis is generated on every training run in `reports/threshold_report.json`, including fixed threshold points and top-k alert volumes (`alerts_per_10k`) to support review-capacity decisions.

Artifacts produced for reproducibility:

- `artifacts/models/fraud_model.pkl` (pipeline with preprocessing + model)
- `artifacts/preprocessors/preprocessor.pkl`
- `artifacts/models/feature_columns.json`
- `artifacts/models/run_metadata.json` (run id, config/data fingerprints, feature schema, split/sample metadata, versions)
- `reports/threshold_report.json` (precision/recall/alerts tradeoffs by threshold)
- `reports/model_metrics.json` (includes model name, threshold, and train/test shapes)

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
uvicorn src.api.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Model metadata:

```bash
curl http://127.0.0.1:8000/model/metadata
```

Single prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "transaction": {
      "TransactionAmt": 120.5,
      "ProductCD": "W",
      "card1": 1000
    }
  }'
```

Batch prediction:

```bash
curl -X POST http://127.0.0.1:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      {"TransactionAmt": 120.5, "ProductCD": "W", "card1": 1000},
      {"TransactionAmt": 5.0, "ProductCD": "H", "card1": 2345}
    ]
  }'
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Phase 4 Dashboard

Start the API first:

```bash
python -m uvicorn src.api.main:app --reload
```

Then start the dashboard in a second terminal:

```bash
streamlit run dashboard/app.py
```

Optional API URL override:

```bash
API_BASE_URL=http://127.0.0.1:8000 streamlit run dashboard/app.py
```

Dashboard default URL:

```text
http://localhost:8501
```

The dashboard provides:

- API health status (`/health`)
- Model metadata and artifact availability (`/model/metadata`)
- Single transaction prediction (`/predict`)
- Optional batch prediction (`/predict/batch`)
- Local model metrics from `reports/model_metrics.json` when available
- Local threshold report from `reports/threshold_report.json` when available

## Phase 5 Alert Engine

Phase 5 adds a lightweight, rule-based alert engine for fraud risk operations.
It converts prediction outputs (`risk_score`, `predicted_label`, `severity`) into
actionable alerts with reason codes and recommended actions.

Alert fields include:

- `alert_id`
- `timestamp`
- `risk_score`
- `predicted_label`
- `severity` (`low`, `medium`, `high`, `critical`)
- `status`
- `reason_codes`
- `recommended_action`
- transaction snapshot

Storage is local JSONL for development/demo:

- `reports/alerts.jsonl`

### API endpoints

Get recent alerts:

```bash
curl http://127.0.0.1:8000/alerts
```

Evaluate and persist one alert:

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "transaction": {
      "TransactionAmt": 120.5,
      "ProductCD": "W",
      "card1": 1000
    }
  }'
```

### Dashboard alert panel

Start API:

```bash
python -m uvicorn src.api.main:app --reload
```

Start dashboard:

```bash
python -m streamlit run dashboard/app.py
```

The dashboard includes:

- Recent alerts table from `GET /alerts`
- Sample alert generation via `POST /alerts/evaluate`

## Phase 6 Local Production Readiness

Phase 6 adds local production-readiness tooling so the platform is easier to run,
test, and demo with consistent commands.

### Run Locally With Make

Install dependencies:

```bash
make install
```

Run API:

```bash
make api
```

Run dashboard:

```bash
make dashboard
```

Run tests:

```bash
make test
```

### Run With Docker Compose

Build/start services:

```bash
make docker-up
```

Stop services:

```bash
make docker-down
```

View logs:

```bash
make docker-logs
```

The dashboard container uses:

- `API_BASE_URL=http://api:8000`

### Local URLs

- API: `http://127.0.0.1:8000`
- Dashboard: `http://127.0.0.1:8501`
- API docs: `http://127.0.0.1:8000/docs`

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

1. Start the API with `python -m uvicorn src.api.main:app --reload`.
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
