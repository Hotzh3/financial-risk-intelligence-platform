# Portfolio Pitch

## 30-Second Pitch
I built an end-to-end Financial Risk Intelligence Platform using the IEEE-CIS fraud dataset. It covers data cleaning, leak-safe feature engineering, reproducible scikit-learn modeling, a FastAPI prediction service, a Streamlit monitoring dashboard, and a rule-based alert engine. The project is Dockerized and CI-tested for clean local reproducibility.

## 2-Minute Pitch
This project simulates a local, production-inspired fraud risk workflow. I start from raw transaction data, build deterministic features with leakage controls, and train a reproducible sklearn pipeline centered on logistic regression for interpretable baseline performance. I evaluate with precision, recall, F1, ROC-AUC, and PR-AUC, and I publish threshold trade-offs to connect model behavior with analyst review capacity.

On the serving side, I expose prediction and metadata endpoints via FastAPI, then consume them in a Streamlit dashboard that shows API health, model context, single/batch scoring, metrics, threshold tables, and alerts. I added a rule-based alert layer to translate risk outputs into reason codes and recommended actions, with local JSONL persistence for auditability. The repository includes Docker Compose, Makefile workflows, and CI tests, so anyone can run and validate it quickly.

## Technical Pitch
- Deterministic feature build with explicit anti-leakage exclusions
- Training/inference parity through `Pipeline` + `ColumnTransformer`
- Artifact consistency checks during inference
- Fraud-focused metric selection and threshold reporting
- Typed API contracts and dependency-injected service layer
- Local alert persistence for transparent rule outcomes

## Recruiter-Friendly Pitch
This is a complete machine-learning product prototype, not just a notebook. It demonstrates the ability to go from data work to deployable API, user-facing dashboard, and operational alerting with clean documentation and reproducible developer workflows.

## Fintech/Banking-Focused Pitch
The platform emphasizes practical fraud operations: class-imbalance-aware modeling, controllable risk thresholds, explainable alert reasons, and analyst-friendly outputs. It is intentionally honest about scope: local demo architecture, production-inspired patterns, no claims of live banking integration.
