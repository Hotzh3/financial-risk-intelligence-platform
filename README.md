# Financial Risk Intelligence Platform

End-to-end fraud risk intelligence platform built on the IEEE-CIS Fraud Detection dataset. The project demonstrates a full local workflow from data preparation and leak-safe feature engineering to reproducible scikit-learn modeling, FastAPI inference endpoints, a Streamlit monitoring dashboard, and a rule-based alert engine. It is designed as a portfolio-ready, production-inspired system for technical interviews and internship applications.

[![CI](https://github.com/Hotzh3/financial-risk-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/Hotzh3/financial-risk-intelligence-platform/actions/workflows/ci.yml)

## Stack

- Python
- pandas
- scikit-learn
- FastAPI
- Streamlit
- Docker + Docker Compose
- GitHub Actions

## Architecture

```text
Raw Transactions
→ Data Pipeline
→ Feature Engineering
→ ML Risk Model
→ FastAPI Prediction Service
→ Streamlit Dashboard
→ Alert Engine
→ Local JSONL Alert Storage
```

`docker-compose.yml` runs API + dashboard together for local demo usage.

## Key Features

- Leak-safe data and feature pipeline (target and leakage columns excluded)
- Reproducible scikit-learn training pipeline (`Pipeline` + `ColumnTransformer`)
- Fraud-appropriate metrics (precision, recall, F1, ROC-AUC, PR-AUC)
- Threshold tradeoff reporting for alert review capacity
- FastAPI prediction and metadata endpoints
- Streamlit dashboard for model operations and scoring
- Rule-based alert engine with reason codes and actions
- Docker/Makefile local production-readiness workflow
- CI test execution via GitHub Actions

## Quickstart

### Local

```bash
make install
make test
make api
make dashboard
```

### Docker

```bash
make docker-up
make docker-down
make docker-logs
```

### URLs

- API: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8501

## Demo Preview

Add screenshots manually after running the app. Suggested files:

- `docs/assets/dashboard_overview.png`
- `docs/assets/api_docs.png`
- `docs/assets/alert_engine.png`
- `docs/assets/model_metrics.png`

Capture guidance is available in `docs/screenshots_checklist.md` and `docs/assets/README.md`.

## Demo Flow

1. Start API (`make api`)
2. Start dashboard (`make dashboard`)
3. Open API docs (`http://127.0.0.1:8000/docs`)
4. Run single prediction (`POST /predict`)
5. Generate alert (`POST /alerts/evaluate`)
6. Show metrics + threshold report (`reports/model_metrics.json`, `reports/threshold_report.json`)
7. Explain Docker/Makefile commands (`make docker-up`, `make docker-logs`, `make docker-down`)

For speaker notes and fallback steps, see `docs/demo_script.md`.

## Project Structure

```text
src/
  data/        # load/clean pipeline
  features/    # feature build and leakage controls
  models/      # train/evaluate/predict and artifact metadata
  api/         # FastAPI app, routes, schemas, services
  alerts/      # alert rules, engine, JSONL storage

dashboard/     # Streamlit app and UI helpers
docs/          # architecture, modeling, API, dashboard, alerts, and portfolio materials
reports/       # metrics + threshold reports (generated)
config/        # YAML configuration
tests/         # unit/integration tests
```

## Model

- Dataset: IEEE-CIS Fraud Detection (Kaggle)
- Target: `isFraud`
- Problem type: binary classification
- Baseline model: logistic regression (configured in `config/config.yaml`)
- Optional model path: anomaly model artifact generation (Isolation Forest) if enabled
- Preprocessing: imputation, scaling, one-hot encoding through `ColumnTransformer` inside a training `Pipeline`
- Leakage prevention: excludes `TransactionID`, target, and configured drop columns from model features
- Reported metrics: precision, recall, F1, ROC-AUC, PR-AUC
- Accuracy is not the primary metric due to class imbalance in fraud detection

## API

- `GET /health`
- `GET /model/metadata`
- `POST /predict`
- `POST /predict/batch`
- `GET /alerts`
- `POST /alerts/evaluate`

Example requests:

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}'
```

## Dashboard

The dashboard (`dashboard/app.py`) provides:

- API health status
- Model metadata and artifact availability
- Single prediction form
- Batch prediction input
- Model metrics panel
- Threshold report panel
- Alerts panel and sample alert generation

## Alert Engine

- Rule-based alert generation from transaction + risk signals
- Reason codes (for example `HIGH_RISK_SCORE`, `MODEL_FLAGGED_FRAUD`)
- Severity-based recommended actions
- Local JSONL storage via `AlertStorage`
- `reports/alerts.jsonl` is generated at runtime and git-ignored

## Docker and CI

- `Dockerfile`: app image for API/dashboard runtime
- `docker-compose.yml`: local multi-service orchestration (API + dashboard)
- `.dockerignore`: reduces build context size
- `.github/workflows/ci.yml`: installs dependencies and runs `pytest -q`

## Why This Project Matters

- Demonstrates data engineering fundamentals for structured risk data
- Shows ML engineering with reproducible training/inference artifacts
- Includes backend API design and contract-based prediction access
- Adds product-thinking via dashboard UX for analysts
- Implements business logic through interpretable alert rules
- Demonstrates local production-readiness with Docker and CI workflows
- Reflects professional Git hygiene and artifact boundaries

## Portfolio Links / Materials

- `docs/portfolio_pitch.md`
- `docs/linkedin_post.md`
- `docs/cv_bullets.md`
- `docs/interview_guide.md`
- `docs/demo_script.md`

## Documentation Index

- `docs/architecture.md`
- `docs/modeling.md`
- `docs/api.md`
- `docs/dashboard.md`
- `docs/alerts.md`
- `docs/project_decisions.md`
- `docs/interview_guide.md`
- `docs/demo_script.md`
- `docs/screenshots_checklist.md`
- `docs/release_notes_v1.md`
- `docs/assets/README.md`
