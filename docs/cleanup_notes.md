# Cleanup Notes (Phase 9)

## Removed

- Legacy top-level `api/` package (old `/api/v1` implementation with deprecated Pydantic examples and SQLite alert wiring).
- Obsolete `src/alerts/alert_engine.py` (legacy SQLite-based alert engine not used by current API/service stack).

## Why It Was Safe

- Active runtime uses `src/api/*` and `src/alerts/engine.py`/`rules.py`/`storage.py`.
- Test imports were migrated away from legacy `api.*` paths.
- No current docs or commands rely on `api.main` anymore.

## Updated for Consistency

- `tests/test_prediction_features.py` now validates active inference input alignment (`src.models.predict._prepare_input`).
- `tests/README.md` no longer references `api.*` imports.
- `docs/screenshots/README.md` now uses active commands:
  - `python -m uvicorn src.api.main:app --reload`
  - `python -m streamlit run dashboard/app.py`

## Intentionally Kept

- `src/api` and `src/alerts` active modules.
- Existing generated report files under `reports/` used by dashboard/docs.
- Docker/Makefile/CI structure and Phase 8 portfolio docs.

## Remaining Notes

- No Pydantic deprecation warnings remain in tests after removing legacy `api/schemas/models.py`.
- No Streamlit `use_container_width` deprecation warning was observed in current test run.
