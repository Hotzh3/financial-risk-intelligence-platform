# Screenshots Checklist

Capture screenshots manually after running API and dashboard.

## 1) README / Repo Landing
- Filename: `repo_landing.png`
- Where: GitHub repository main page
- Run first: push docs updates to your branch
- Visible: project title, short summary, key docs links
- Why it matters: first-impression professionalism

## 2) API Health Endpoint
- Filename: `api_health_response.png`
- Where: terminal or browser call to `GET /health`
- Run first: `make api`
- Visible: `{"status":"ok","service":"financial-risk-intelligence-api"}`
- Why it matters: service reliability signal

## 3) FastAPI Swagger Docs
- Filename: `api_docs.png`
- Where: `http://127.0.0.1:8000/docs`
- Run first: `make api`
- Visible: endpoint list (`/health`, `/predict`, `/alerts`)
- Why it matters: clear API contract and backend quality

## 4) Model Metadata Response
- Filename: `model_metadata_response.png`
- Where: Swagger or curl for `GET /model/metadata`
- Run first: `make api`
- Visible: model name, threshold, feature count, artifact checks
- Why it matters: reproducibility and artifact governance

## 5) Dashboard Top Section
- Filename: `dashboard_overview.png`
- Where: `http://127.0.0.1:8501`
- Run first: `make dashboard`
- Visible: title, API Health, Model Metadata blocks
- Why it matters: product-facing monitoring capability

## 6) Single Prediction Result
- Filename: `single_prediction_result.png`
- Where: dashboard single prediction panel
- Run first: `make api` and `make dashboard`
- Visible: input form + returned severity/risk score/label
- Why it matters: end-to-end inference proof

## 7) Model Metrics Chart
- Filename: `model_metrics.png`
- Where: dashboard metrics panel
- Run first: `make dashboard`
- Visible: precision/recall/F1/ROC-AUC/PR-AUC + chart
- Why it matters: fraud-aware evaluation discipline

## 8) Threshold Report
- Filename: `threshold_report.png`
- Where: dashboard threshold section
- Run first: `make dashboard`
- Visible: threshold rows including alerts-per-10k
- Why it matters: operational trade-off thinking

## 9) Alerts Section With Generated Alert
- Filename: `alert_engine.png`
- Where: dashboard alerts panel
- Run first: click "Generate Alert From Sample Transaction"
- Visible: alert row with severity, reason codes, action
- Why it matters: explainable business logic, not just model score

## 10) Docker/Makefile Commands
- Filename: `docker_commands_terminal.png`
- Where: terminal session
- Run first: `make help`, `make docker-up`, `make docker-logs`
- Visible: command output proving local production-readiness
- Why it matters: engineering maturity and reproducible setup
