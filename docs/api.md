# API

## Purpose

The FastAPI service exposes model metadata, fraud-risk predictions, and alert evaluation/listing for local operations.

Base URL: `http://127.0.0.1:8000`

## Endpoints

### `GET /health`

Response:

```json
{"status":"ok","service":"financial-risk-intelligence-api"}
```

### `GET /model/metadata`

Returns model name, target, feature count, threshold, and artifact existence flags.

### `POST /predict`

Request:

```json
{"transaction":{"TransactionAmt":120.5,"ProductCD":"W","card1":1000}}
```

Response:

```json
{"risk_score":0.73,"predicted_label":1,"severity":"medium"}
```

### `POST /predict/batch`

Request:

```json
{"transactions":[{"TransactionAmt":120.5,"ProductCD":"W","card1":1000},{"TransactionAmt":5.0,"ProductCD":"H","card1":2345}]}
```

Response shape:

```json
{"predictions":[{"risk_score":0.73,"predicted_label":1,"severity":"medium"}]}
```

### `GET /alerts?limit=20`

Returns recent alert objects from local JSONL storage.

### `POST /alerts/evaluate`

Evaluates rules for a transaction and persists a new alert.

Request:

```json
{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}
```

## cURL Examples

```bash
curl http://127.0.0.1:8000/health
```

```bash
curl http://127.0.0.1:8000/model/metadata
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
curl 'http://127.0.0.1:8000/alerts?limit=20'
```

```bash
curl -X POST http://127.0.0.1:8000/alerts/evaluate \
  -H "Content-Type: application/json" \
  -d '{"transaction":{"TransactionAmt":1500,"ProductCD":"W","card1":7777},"risk_score":0.97,"predicted_label":1}'
```

## Artifact Usage

The API reads model artifacts and metadata generated during training:

- `artifacts/models/fraud_model.pkl`
- `artifacts/models/feature_columns.json`
- `artifacts/models/run_metadata.json`
- `reports/model_metrics.json`

If required artifacts are missing or inconsistent, prediction endpoints return an error status.
