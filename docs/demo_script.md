# Demo Script

## 1. Start API

```bash
make api
```

## 2. Start Dashboard (new terminal)

```bash
make dashboard
```

## 3. Open API Docs

- http://127.0.0.1:8000/docs

## 4. Run Prediction

Use Swagger or curl:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}'
```

Call out `risk_score`, `predicted_label`, and `severity`.

## 5. Generate Alert

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}'
```

Then fetch recent alerts:

```bash
curl 'http://127.0.0.1:8000/alerts?limit=5'
```

## 6. Explain Metrics

Open `reports/model_metrics.json` and `reports/threshold_report.json`.

- Explain why PR-AUC and recall are key under class imbalance
- Explain threshold tradeoff using alerts-per-10k rows

## 7. Explain Docker Commands

```bash
make docker-up
make docker-logs
make docker-down
```

Mention that Compose runs API + dashboard together for local reproducibility.
