# Demo Script (3-5 Minutes)

## 0) Setup (15s)
Say: "This is a local, production-inspired fraud risk platform. I’ll show model serving, monitoring, and alerting in under five minutes."

Run:

```bash
make help
make test
```

## 1) Start API (30s)
Say: "First I start the FastAPI prediction service."

```bash
make api
```

Open: `http://127.0.0.1:8000/docs`

Click/Highlight:
- `GET /health`
- `GET /model/metadata`
- `POST /predict`
- `POST /alerts/evaluate`

## 2) Start Dashboard (30s)
Say: "Now I open the operations dashboard that consumes these endpoints."

In a second terminal:

```bash
make dashboard
```

Open: `http://127.0.0.1:8501`

Click/Highlight:
- API Health panel
- Model Metadata panel

## 3) Run Prediction (45s)
Say: "I’ll score one transaction and review risk output."

Use Swagger or terminal:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}'
```

What to say:
- "`risk_score` is the model probability-style risk signal."
- "`predicted_label` is thresholded output."
- "`severity` maps risk to operational triage bands."

## 4) Generate Alert (45s)
Say: "Next I convert prediction output into an analyst-facing alert."

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}'
```

Then:

```bash
curl 'http://127.0.0.1:8000/alerts?limit=5'
```

What to say:
- "Each alert includes severity, reason codes, and recommended action."

## 5) Show Metrics + Threshold Trade-Offs (45s)
Say: "For fraud, accuracy is secondary to precision/recall and operational review volume."

In dashboard:
- Model Metrics panel
- Threshold Report panel

Reference:
- `reports/model_metrics.json`
- `reports/threshold_report.json`

## 6) Local Production Readiness (30s)
Say: "The project is reproducible with Make targets, Docker Compose, and CI tests."

```bash
make docker-up
make docker-down
```

## Fallbacks

If API fails:
- run `make install`
- re-run `make api`

If dashboard fails:
- ensure API is live at `http://127.0.0.1:8000/health`
- set `API_BASE_URL=http://127.0.0.1:8000`
- re-run `make dashboard`

If Docker fails:
- continue demo via local `make api` + `make dashboard`

## End the Demo (15s)
Say: "This project demonstrates end-to-end ML engineering: data pipeline, reproducible modeling, API serving, operational dashboard, alerting logic, and developer-ready local deployment."
