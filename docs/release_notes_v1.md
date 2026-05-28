# Release Notes v1.0

## Version
- `v1.0.0` (portfolio release)

## What Is Included

- Data loading, cleaning, and EDA-ready workflow
- Leak-safe feature engineering pipeline
- Reproducible sklearn modeling pipeline and metrics artifacts
- Threshold trade-off reporting (`reports/threshold_report.json`)
- FastAPI prediction service (`/health`, `/model/metadata`, `/predict`, `/predict/batch`, `/alerts`, `/alerts/evaluate`)
- Streamlit monitoring dashboard for operations and scoring
- Rule-based alert engine with local JSONL persistence
- Local production-readiness assets: Dockerfile, Docker Compose, Makefile, `.env.example`
- CI workflow running `pytest -q`
- Portfolio/interview documentation package

## How To Run

```bash
make install
make test
make api
make dashboard
```

Docker option:

```bash
make docker-up
make docker-down
```

## What Was Validated

- `pytest` test suite passes locally
- Docker Compose configuration is valid (`docker compose config`)
- Make targets for setup/test/run are documented and available
- Git ignore boundaries are in place for secrets/data/artifacts/logs

## Known Limitations

- Local deployment only (no cloud deployment in scope)
- No authentication/authorization
- No managed production database
- No real-time streaming pipeline
- No external paid services or outbound alert channels enabled by default

## Future Work

- Probability calibration and cost-sensitive threshold optimization
- Enhanced temporal validation and drift monitoring
- Security hardening and observability for production deployment scope
- Managed persistence beyond JSONL for multi-user operations
