# Release Notes v1.0

## Summary
Version 1.0 delivers a local, end-to-end Financial Risk Intelligence Platform for fraud-risk scoring and monitoring.

## Included in v1.0

- Data pipeline: loading, cleaning, and EDA-ready workflow
- Feature engineering: deterministic, leak-safe feature table build
- Model: reproducible sklearn baseline with threshold reporting
- API: FastAPI endpoints for health, metadata, predictions, and alerts
- Dashboard: Streamlit interface for scoring, metrics, thresholds, and alerts
- Alerts: rule-based severity/reason/action generation with JSONL storage
- Local readiness: Dockerfile, Docker Compose, Makefile, `.env.example`
- CI: GitHub Actions pytest execution
- Documentation: architecture, modeling, API, dashboard, alerts, interview guide, demo materials

## Known Limitations

- Local deployment only (no cloud deployment in scope)
- No authentication/authorization
- No managed database or distributed storage
- No real-time streaming pipeline
- No external notification channels enabled by default

## Next Improvements

- Add probability calibration and cost-sensitive threshold recommendations
- Expand temporal validation and drift analysis
- Add production security and observability hardening when deployment scope expands
- Evolve persistence beyond JSONL for multi-user operational workflows
