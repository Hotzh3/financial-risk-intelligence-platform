# Screenshots and Demo Assets

Use this folder for portfolio-ready screenshots, short demo GIFs, or annotated images that show the platform in action.

Recommended assets to add over time:

- `api-docs.png` — FastAPI Swagger UI at `http://127.0.0.1:8000/docs`.
- `dashboard-overview.png` — Streamlit dashboard overview and KPIs.
- `alert-monitoring.png` — Alert list, severity distribution, and threshold controls.
- `prediction-demo.png` — Example transaction scoring result.

Generated exploratory analysis figures currently live in `reports/` and can also be referenced from the README until dedicated product screenshots are captured.

## Suggested capture flow

1. Start the API:

   ```bash
   uvicorn api.main:app --reload
   ```

2. Open the API docs:

   ```text
   http://127.0.0.1:8000/docs
   ```

3. Start the dashboard:

   ```bash
   streamlit run dashboard/app.py
   ```

4. Capture screenshots and save them in this directory with clear names.
