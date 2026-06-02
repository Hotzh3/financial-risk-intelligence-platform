# Dashboard

## Purpose

The Streamlit dashboard provides a compact operations view for API status, model context, scoring workflows, threshold analysis, and alerts.

## Run

```bash
make dashboard
```

Default URL: `http://127.0.0.1:8501`

Set API URL if needed:

```bash
export API_BASE_URL=http://127.0.0.1:8000
```

## Guided Sections

- `How this demo works`: explains the local portfolio-demo workflow, data source, API serving, and alerting context
- `Where do the data fields come from?`: explains the subset of IEEE-CIS fields used in the form
- `Why this result?`: explains risk score, threshold, predicted label, and severity after scoring
- `How to read alerts`: explains reason codes, recommended action, and severity as operational context
- `How to read these metrics`: explains recall, precision, F1, ROC-AUC, and PR-AUC
- `How to read threshold trade-offs`: explains how threshold choice affects alerts, recall, and false positives
- `Known limitations of this demo`: clarifies the local-demo scope and non-production assumptions

## Panels

- Sidebar: project context, API status, quick links, and demo steps
- Operational Snapshot: KPI row for API status, model, feature count, threshold, alerts count
- API Health: confirms API availability and configured base URL
- Model Metadata: model name, target, feature count, threshold, artifact checks
- Single Prediction: form-based scoring with severity output plus a threshold-based explanation
- Batch Prediction: optional JSON list input for multiple records
- Alerts: list recent alerts, explain rule-based context, and generate a sample alert
- Model Metrics: displays precision/recall/F1/ROC-AUC/PR-AUC/threshold with metric guidance
- Threshold Report: displays threshold rows from report JSON with trade-off guidance

## Notes

- Dashboard depends on API endpoints for live requests.
- Metrics/threshold panels read local report JSON files from `reports/`.
