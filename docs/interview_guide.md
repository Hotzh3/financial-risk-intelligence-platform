# Interview Guide

## Explain This Project in 2 Minutes
This is an end-to-end fraud risk intelligence platform using the IEEE-CIS dataset. I built a leak-safe feature pipeline, trained a reproducible scikit-learn baseline model, exposed prediction endpoints through FastAPI, added a Streamlit monitoring dashboard, and implemented a rule-based alert engine that stores analyst-ready alerts locally as JSONL. The project is Dockerized, test-covered, and CI-validated for local production-readiness.

## Explain the Architecture
- Offline: load/clean data, build features, train model, generate reports/artifacts
- Online-style: API loads artifacts and serves scoring endpoints
- Analyst layer: dashboard reads API + reports
- Alerting layer: rules convert scores/fields into reason-coded alerts

## Defend ML Choices
- Logistic regression is a transparent, strong baseline for tabular fraud data
- Pipeline + ColumnTransformer ensure reproducible preprocessing at train/infer time
- Class imbalance is handled with class weighting and threshold analysis

## Defend Threshold Tuning
- Threshold is operational, not just statistical
- `threshold_report.json` compares precision/recall and alert volumes
- Top-k style thresholds link model behavior to review capacity

## Explain API, Dashboard, and Alerts
- API: health, metadata, single/batch predict, alert evaluate/list
- Dashboard: operations interface for health, predictions, metrics, thresholds, alerts
- Alerts: deterministic reason codes + severity-driven recommended actions

## Questions Recruiters May Ask
- Why is this project relevant for fintech roles?
- What part did you build end-to-end yourself?
- How did you keep the project production-inspired while staying local?
- What did you learn from integrating API + dashboard + alerting?

## Technical Questions Engineers May Ask
- How do you prevent feature leakage?
- How do you guarantee train/inference feature consistency?
- Why logistic regression over tree-based models for baseline?
- How do you choose the operating threshold in imbalanced fraud tasks?
- What failure modes exist if artifacts are missing or mismatched?

## Trade-Offs
- Simplicity and transparency over model complexity
- Local JSONL persistence over managed database complexity
- Fast portfolio iteration over full production hardening
- Deterministic alert rules over dynamic policy engines

## Known Limitations
- Local-only deployment pattern
- No auth/authorization layer
- No cloud infra or managed database
- Rule engine is simple and deterministic
- No live event streaming
- No external email/webhook alert delivery enabled by default

## Future Improvements
- Add model calibration and threshold recommendation by explicit cost matrix
- Expand temporal validation and drift monitoring
- Add secure deployment hardening (auth, secrets management, observability)
- Replace JSONL with managed persistence when moving beyond local demo scope
