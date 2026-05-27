# Portfolio Pitch

## 30-Second Pitch
I built an end-to-end Financial Risk Intelligence Platform using the IEEE-CIS fraud dataset. It includes leak-safe feature engineering, reproducible scikit-learn modeling, a FastAPI prediction service, a Streamlit monitoring dashboard, and a rule-based alert engine. It is Dockerized and CI-tested for local reproducibility.

## 2-Minute Pitch
This project simulates a local, production-inspired fraud-risk workflow. I start from raw transaction data, build deterministic features with leakage controls, and train a reproducible sklearn pipeline centered on logistic regression as an interpretable baseline. I evaluate with precision, recall, F1, ROC-AUC, and PR-AUC, and I generate threshold trade-off reports to align model behavior with review capacity.

On the serving side, I expose prediction and metadata endpoints through FastAPI, then consume them in a Streamlit dashboard for API health, model context, scoring, metrics, threshold views, and alerts. I added a rule-based alert layer that translates model output into severity, reason codes, and recommended actions with local JSONL persistence. Docker Compose, Makefile targets, and CI tests make the repo easy to run and review.

## Technical Pitch
- Leak-safe feature build with explicit exclusion controls
- Training/inference parity using `Pipeline` + `ColumnTransformer`
- Artifact consistency checks during prediction
- Fraud-focused metrics and threshold reporting
- Typed API contracts and modular service layer
- Explainable alert rules with deterministic behavior

## Recruiter-Friendly Pitch
This is a complete ML product prototype, not only a modeling notebook. It demonstrates data engineering, model serving, backend API design, dashboard UX, alerting logic, and practical repo hygiene.

## Fintech/Banking-Focused Pitch
The platform emphasizes operational fraud needs: class-imbalance-aware evaluation, controllable thresholds, explainable alert reasons, and analyst-friendly outputs. Scope is intentionally honest: local demo architecture without claims of production banking integration.
