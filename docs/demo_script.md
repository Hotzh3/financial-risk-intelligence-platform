# Demo Script (3-5 Minutes)

## Primary Demo Path

Start the full demo from one terminal:

```bash
make demo
```

Open the dashboard at `http://127.0.0.1:8501`.

Say: "This is a local, production-inspired fraud risk platform. I’ll show model serving, monitoring, and alerting in under five minutes."

## Presentation Flow

### 1) Open the dashboard

Say: "This dashboard is the operations view for the fraud-risk workflow."

Highlight:
- `How this demo works`
- `Operational Snapshot`
- API status and model threshold

### 2) Explain how the demo works

Say: "The model was trained offline on the IEEE-CIS Fraud Detection dataset, then served through FastAPI."

Highlight:
- Local portfolio demo
- Dashboard sends transactions to the API
- Alert engine adds operational context with reason codes and actions

### 3) Run a prediction

Use the dashboard form or Swagger:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}'
```

What to say:
- `risk_score` is the model-estimated fraud risk score.
- `predicted_label` is thresholded output.
- `severity` maps risk into low / medium / high / critical.

### 4) Explain why the result happened

Open the `Why this result?` expander in the dashboard.

What to say:
- The score is compared against the configured threshold.
- `predicted_label = 1` means the model flagged potential fraud.
- `predicted_label = 0` means the model did not flag fraud.
- The decision combines model output plus configured thresholds.

### 5) Generate an alert

Click `Generate Alert From Sample Transaction` or call:

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
- Alerts are not raw model predictions only.
- They include `reason_codes`, `recommended_action`, and `severity`.
- Reason codes are rule-based so the result is easier to review.

### 6) Explain metrics and thresholds

In the dashboard, open:
- `How to read these metrics`
- `How to read threshold trade-offs`

What to say:
- Recall is about catching fraud cases.
- Precision is about reducing false positives.
- Lower thresholds create more alerts and higher recall.
- Higher thresholds create fewer alerts and potentially higher precision.
- Threshold choice is a business decision, not only a model decision.

### 7) Show API docs

Open `http://127.0.0.1:8000/docs`

Highlight:
- `GET /health`
- `GET /model/metadata`
- `POST /predict`
- `POST /alerts/evaluate`

## Fallbacks

If you want the manual local path instead:

```bash
make api
make dashboard
```

If Docker is preferred:

```bash
make demo-docker
```

If API fails:
- run `make install`
- re-run `make api`

If dashboard fails:
- ensure API is live at `http://127.0.0.1:8000/health`
- set `API_BASE_URL=http://127.0.0.1:8000`
- re-run `make dashboard`

## End the Demo

Say: "This project demonstrates end-to-end ML engineering: data pipeline, reproducible modeling, API serving, an operational dashboard, alerting logic, and developer-ready local deployment."
