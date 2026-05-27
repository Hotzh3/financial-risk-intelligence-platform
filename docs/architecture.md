# Architecture

## End-to-End Flow

```text
Raw Transactions
→ Data Pipeline
→ Feature Engineering
→ ML Risk Model
→ FastAPI Prediction Service
→ Streamlit Dashboard
→ Alert Engine
→ Local JSONL Alert Storage
```

The platform is local-first and production-inspired. It combines offline model development with online-style inference and analyst-facing monitoring.

## Data Flow

1. Raw IEEE-CIS transaction data is loaded and cleaned.
2. `src/features/build_features.py` creates a leak-safe feature table.
3. `src/models/train.py` trains a scikit-learn pipeline and writes artifacts/reports.
4. `src/api` loads artifacts and serves prediction endpoints.
5. `dashboard/app.py` consumes API endpoints and reads report files.
6. `src/alerts` evaluates risk/severity rules and appends JSONL alert records.

## Separation of Concerns

- `src/data`: ingestion and cleaning only
- `src/features`: deterministic feature construction and exclusions
- `src/models`: training, evaluation, and artifact consistency
- `src/api`: request/response contracts and service orchestration
- `src/alerts`: rule logic and storage mechanics
- `dashboard`: analyst workflow and visibility layer
- `reports`: generated model/threshold outputs for monitoring

## Runtime Topology

- Local mode: API and dashboard run as separate processes.
- Container mode: Docker Compose runs API + dashboard together.
- Storage mode: alert records persist locally at `reports/alerts.jsonl`.
