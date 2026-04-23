# Financial Risk Intelligence Platform

> An end-to-end fraud detection system that processes financial transactions,
> detects anomalies using machine learning, exposes results via REST API,
> and visualizes risk insights through an operational dashboard.

## Problem Statement

Financial institutions process millions of transactions daily. Identifying
fraudulent activity in near real-time is critical to reduce losses and protect
customers. This platform simulates a production-grade fraud detection system
as deployed in fintech companies.

## System Architecture

[Raw Transactions] → [Data Pipeline] → [Feature Engineering]  
↓  
[Anomaly Detection Model]  
↓  

┌────────────────────┼───────────────────┐  
↓                    ↓                   ↓  

[FastAPI REST]       [Streamlit]         [Alert Engine]  

/predict             Dashboard           Email/Webhook  
/transactions        KPIs  
/alerts  


## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Data Processing | Pandas + Polars | Industry standard + modern performance |
| Machine Learning | Scikit-learn + MLflow | Isolation Forest, experiment tracking |
| API | FastAPI | Async, typed, auto Swagger docs |
| Dashboard | Streamlit | Rapid operational UI |
| Database | SQLite → PostgreSQL | Dev-to-prod progression |
| Containers | Docker | Reproducible deployment |

## Project Roadmap

- [x] Phase 0 — Repository structure & setup
- [ ] Phase 1 — Data Engineering + EDA
- [ ] Phase 2 — Feature Engineering + Model
- [ ] Phase 3 — REST API (FastAPI)
- [ ] Phase 4 — Dashboard (Streamlit)
- [ ] Phase 5 — Alert Engine
- [ ] Phase 6 — Deploy (Docker + Cloud)

## Dataset

[IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection)
— 590K anonymized real-world transactions with device and network features.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/financial-risk-intelligence-platform
cd financial-risk-intelligence-platform

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure
financial-risk-intelligence-platform/
├── data/               # Raw and processed datasets
├── notebooks/          # Exploratory analysis
├── src/
│   ├── data/           # Ingestion and cleaning pipeline
│   ├── features/       # Feature engineering
│   ├── models/         # Training and evaluation
│   └── utils/          # Shared utilities
├── api/                # FastAPI application
├── dashboard/          # Streamlit dashboard
└── tests/              # Unit and integration tests

## Author

**Jose** — Data Science & Engineering Portfolio  
[LinkedIn] https://www.linkedin.com/in/jos%C3%A9-gerardo-malfavaun-gorostizaga/

[GitHub] https://github.com/Hotzh3
