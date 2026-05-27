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

## Project Structure

```text
src/
  data/        # load/clean pipeline
  features/    # feature build and leakage controls
  models/      # train/evaluate/predict and artifact metadata
  api/         # FastAPI app, routes, schemas, services
  alerts/      # alert rules, engine, JSONL storage

dashboard/     # Streamlit app and UI helpers
docs/          # architecture, modeling, API, dashboard, alerts, interview prep
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

```bash
curl -X POST http://127.0.0.1:8000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{"transactions":[{"TransactionAmt":120.5,"ProductCD":"W","card1":1000},{"TransactionAmt":5.0,"ProductCD":"H","card1":2345}]}'
```

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}'
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

Run with:

```bash
make dashboard
```

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

## Interview Defense

See the dedicated guide: [docs/interview_guide.md](/Users/josema/Documents/financial-risk-intelligence-platform/docs/interview_guide.md)

## Documentation Index

- [Architecture](/Users/josema/Documents/financial-risk-intelligence-platform/docs/architecture.md)
- [Modeling](/Users/josema/Documents/financial-risk-intelligence-platform/docs/modeling.md)
- [API](/Users/josema/Documents/financial-risk-intelligence-platform/docs/api.md)
- [Dashboard](/Users/josema/Documents/financial-risk-intelligence-platform/docs/dashboard.md)
- [Alerts](/Users/josema/Documents/financial-risk-intelligence-platform/docs/alerts.md)
- [Project Decisions](/Users/josema/Documents/financial-risk-intelligence-platform/docs/project_decisions.md)
- [Interview Guide](/Users/josema/Documents/financial-risk-intelligence-platform/docs/interview_guide.md)
- [Demo Script](/Users/josema/Documents/financial-risk-intelligence-platform/docs/demo_script.md)
- [Assets Guide](/Users/josema/Documents/financial-risk-intelligence-platform/docs/assets/README.md)
