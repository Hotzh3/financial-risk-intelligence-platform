# Screenshots Checklist

Capture screenshots manually after starting the app.

## Start Commands

```bash
make test
make api
make dashboard
```

Optional Docker run:

```bash
make docker-up
make docker-down
```

## URLs

- API health: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8501

## Required Captures

## 1) Repo Landing
- Filename: `repo_landing.png`
- Where: GitHub repository main page
- Command before capture: push docs branch
- Should show: project title, short summary, docs links
- Why recruiters care: fast credibility check

## 2) API Health
- Filename: `api_health_response.png`
- Where: browser or terminal `GET /health`
- Command before capture: `make api`
- Should show: `{"status":"ok","service":"financial-risk-intelligence-api"}`
- Why recruiters care: service is running and testable

## 3) FastAPI Docs
- Filename: `api_docs.png`
- Where: `http://127.0.0.1:8000/docs`
- Command before capture: `make api`
- Should show: endpoint list and interactive docs
- Why recruiters care: API contract quality

## 4) Model Metadata
- Filename: `model_metadata_response.png`
- Where: Swagger response for `GET /model/metadata`
- Command before capture: `make api`
- Should show: model name, threshold, feature count, artifact statuses
- Why recruiters care: reproducibility and artifact governance

## 5) Dashboard Overview
- Filename: `dashboard_overview.png`
- Where: `http://127.0.0.1:8501`
- Command before capture: `make dashboard`
- Should show: title + API Health + Model Metadata sections
- Why recruiters care: product-facing operational layer

## 6) Single Prediction Result
- Filename: `single_prediction_result.png`
- Where: dashboard single prediction section
- Command before capture: `make api` and `make dashboard`
- Should show: form + returned risk score/predicted label/severity
- Why recruiters care: end-to-end inference proof

## 7) Model Metrics
- Filename: `model_metrics.png`
- Where: dashboard model metrics panel
- Command before capture: `make dashboard`
- Should show: precision, recall, F1, ROC-AUC, PR-AUC, threshold chart area
- Why recruiters care: fraud-aware evaluation discipline

## 8) Threshold Report
- Filename: `threshold_report.png`
- Where: dashboard threshold section
- Command before capture: `make dashboard`
- Should show: threshold rows with alerts-per-10k
- Why recruiters care: operational trade-off reasoning

## 9) Alert Engine Panel
- Filename: `alert_engine.png`
- Where: dashboard alerts section
- Command before capture: click "Generate Alert From Sample Transaction"
- Should show: generated alert with severity, reason codes, recommended action
- Why recruiters care: explainability and business logic integration

## 10) Docker/Make Commands
- Filename: `docker_commands_terminal.png`
- Where: terminal
- Command before capture: `make help`, `make docker-up`, `make docker-down`
- Should show: reproducible local workflow commands
- Why recruiters care: engineering maturity and environment consistency
