# Test Suite

This directory contains the automated tests for the Financial Risk Intelligence Platform.

## Test groups

- `test_alert_engine.py` — unit tests for alert persistence, threshold updates, severity filtering, and stats.
- `test_api_alerts.py` — integration tests for FastAPI health, prediction validation, alert routes, and threshold validation.
- `test_feature_engineering.py` — unit tests for feature engineering helpers and pipeline output shape.
- `test_prediction_features.py` — unit tests for inference-side feature alignment before model prediction.

## Running locally

From the project root:

```bash
python -m pytest -q
```

or:

```bash
pytest -q
```

`pytest.ini` adds the repository root to `PYTHONPATH`, so imports such as `src.*` and `dashboard.*` work consistently locally and in CI.

## CI

GitHub Actions runs the same test command on every push and pull request using `.github/workflows/ci.yml`.
