# Demo Script (3-5 Minutes)

## 0) Setup Check (15s)
Say: "This is a local, production-inspired fraud risk platform. I will show data-to-inference operations in under five minutes."

Command:

```bash
make help
```

## 1) Start API (30s)
Say: "First I start the prediction service."

```bash
make api
```

If it fails:
- Verify virtual env exists
- Run `make install`
- Restart `make api`

## 2) Start Dashboard (30s)
Say: "Now I start the operations dashboard in a separate terminal."

```bash
make dashboard
```

If it fails:
- Confirm API is running on `http://127.0.0.1:8000`
- Set `API_BASE_URL` if needed: `export API_BASE_URL=http://127.0.0.1:8000`
- Restart dashboard

## 3) Open API Docs (30s)
Say: "FastAPI gives us an explicit contract for inference and alert endpoints."

Open: `http://127.0.0.1:8000/docs`

Highlight:
- `GET /health`
- `GET /model/metadata`
- `POST /predict`
- `POST /predict/batch`
- `GET /alerts`
- `POST /alerts/evaluate`

## 4) Run Prediction (45s)
Say: "I’ll score one transaction and inspect risk output."

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}'
```

Call out:
- `risk_score`
- `predicted_label`
- `severity`

## 5) Generate Alert (45s)
Say: "Next I transform risk output into a reason-coded alert for analyst workflow."

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}'
```

Then:

```bash
curl 'http://127.0.0.1:8000/alerts?limit=5'
```

## 6) Show Metrics + Thresholds (45s)
Say: "For fraud, we care more about precision/recall trade-offs than raw accuracy."

Show in dashboard:
- Model Metrics panel
- Threshold Report panel

Reference files:
- `reports/model_metrics.json`
- `reports/threshold_report.json`

## 7) Local Production Readiness (30s)
Say: "The repo is reproducible with Make targets, Docker Compose, and CI tests."

```bash
make docker-up
make docker-logs
make docker-down
```

## Fallback Path (if UI unavailable)
If dashboard is down, demo only with API:
- `GET /health`
- `GET /model/metadata`
- `POST /predict`
- `POST /alerts/evaluate`
- `GET /alerts`

Close with: "The system remains demonstrable end-to-end through API contracts even without the UI."
