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

## Panels

- Sidebar: project context, API status, quick links, and demo steps
- Operational Snapshot: KPI row for API status, model, feature count, threshold, alerts count
- API Health: confirms API availability and configured base URL
- Model Metadata: model name, target, feature count, threshold, artifact checks
- Single Prediction: form-based scoring with severity output
- Batch Prediction: JSON list input for multiple records
- Alerts: list recent alerts and generate a sample alert
- Model Metrics: displays precision/recall/F1/ROC-AUC/PR-AUC/threshold
- Threshold Report: displays threshold rows from report JSON

## Notes

- Dashboard depends on API endpoints for live requests.
- Metrics/threshold panels read local report JSON files from `reports/`.
