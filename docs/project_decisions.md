# Project Decisions

## Why FastAPI

- Typed request/response contracts with Pydantic
- Fast local iteration and automatic docs (`/docs`)
- Clear separation between routes and services

## Why Streamlit

- Rapid, practical UI for analyst-facing workflows
- Minimal frontend overhead for an ML-focused project
- Good fit for portfolio demos and interview walkthroughs

## Why Logistic Regression Baseline

- Strong, interpretable baseline for tabular fraud classification
- Fast training and straightforward threshold control
- Works well with class weighting and probability outputs

## Why PR-AUC and Recall Matter

- Fraud is class-imbalanced; accuracy can be misleading
- PR-AUC reflects precision-recall tradeoffs under imbalance
- Recall is critical to reduce missed fraud events

## Why JSONL Alert Storage

- Local-friendly and dependency-light persistence
- Easy to inspect, append, and reset for demos
- Appropriate for Phase 7 portfolio scope

## Why Docker + Makefile

- Reproducible local runtime setup
- Single-command developer workflows
- Supports CI-like parity in local testing
