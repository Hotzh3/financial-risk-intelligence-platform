"""Streamlit dashboard for Financial Risk Intelligence Platform (Phase 4)."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboard.components.charts import render_metrics_chart, render_threshold_rows
from dashboard.components.metrics import extract_core_metrics, load_json_report
from dashboard.utils.api_client import (
    evaluate_alert,
    get_api_base_url,
    get_alerts,
    get_health,
    get_model_metadata,
    predict_batch,
    predict_one,
)

REPORTS_DIR = Path("reports")
METRICS_PATH = REPORTS_DIR / "model_metrics.json"
THRESHOLD_PATH = REPORTS_DIR / "threshold_report.json"


st.set_page_config(page_title="Financial Risk Intelligence Platform", layout="wide")

api_base_url = get_api_base_url()
health = get_health()
metadata = get_model_metadata()
alerts_payload = get_alerts(limit=20)

is_api_up = "error" not in health
api_status_label = "Online" if is_api_up else "Offline"
api_status_detail = health.get("service", "unreachable") if is_api_up else "check API process"

alerts: list[dict] = []
alerts_error: str | None = None
if "error" in alerts_payload:
    alerts_error = str(alerts_payload["error"])
else:
    alerts = alerts_payload.get("alerts", [])

with st.sidebar:
    st.title("FRIP Dashboard")
    st.caption("Financial Risk Intelligence Platform")
    st.divider()
    st.markdown(f"**API Base URL:** `{api_base_url}`")
    if is_api_up:
        st.success(f"API Status: {api_status_label}")
    else:
        st.error(f"API Status: {api_status_label}")
    st.caption(api_status_detail)

    st.markdown("**Quick Links**")
    st.markdown("- [API Docs](http://127.0.0.1:8000/docs)")
    st.markdown("- [API Health](http://127.0.0.1:8000/health)")
    st.markdown("- [Dashboard](http://127.0.0.1:8501)")

    st.markdown("**Demo Steps**")
    st.markdown("1. Start API (`make api`)")
    st.markdown("2. Start dashboard (`make dashboard`)")
    st.markdown("3. Run single prediction")
    st.markdown("4. Generate sample alert")
    st.markdown("5. Review metrics and thresholds")

st.title("Financial Risk Intelligence Platform")
st.caption("End-to-end fraud risk scoring, monitoring, and alerting dashboard")
st.info("Local demo / portfolio project: production-inspired workflow with local artifacts and services.")

with st.container(border=True):
    st.subheader("Operational Snapshot")
    model_name = "n/a"
    feature_count = "n/a"
    threshold_value = "n/a"
    if "error" not in metadata:
        model_name = metadata.get("model_name") or "n/a"
        feature_count = metadata.get("number_of_features") or "n/a"
        threshold_value = metadata.get("threshold") or "n/a"

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("API Status", api_status_label)
    k2.metric("Model", str(model_name))
    k3.metric("Features", str(feature_count))
    k4.metric("Threshold", str(threshold_value))
    k5.metric("Recent Alerts", str(len(alerts)))

with st.container(border=True):
    st.subheader("API Health")
    if not is_api_up:
        st.warning("API unavailable. Start it with: `python -m uvicorn src.api.main:app --reload`")
        st.caption(f"Configured API_BASE_URL: {api_base_url}")
    else:
        st.success(f"Status: {health.get('status', 'unknown')}")
        st.caption(f"Service: {health.get('service', 'n/a')} | API_BASE_URL: {api_base_url}")

with st.container(border=True):
    st.subheader("Model Metadata")
    if "error" in metadata:
        st.warning(f"Could not load model metadata: {metadata['error']}")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Model", metadata.get("model_name") or "n/a")
        c2.metric("Target", metadata.get("target_column") or "n/a")
        c3.metric("Features", metadata.get("number_of_features") or "n/a")
        c4.metric("Threshold", metadata.get("threshold") or "n/a")

        artifacts = metadata.get("artifacts", {})
        artifact_rows = [
            {
                "artifact": name,
                "path": item.get("path", "n/a"),
                "exists": item.get("exists", False),
            }
            for name, item in artifacts.items()
        ]
        if artifact_rows:
            st.dataframe(artifact_rows, width="stretch", hide_index=True)

with st.container(border=True):
    st.subheader("Single Prediction")
    st.caption("Score one transaction by sending payload to `POST /predict`.")
    st.markdown("- `TransactionAmt`: transaction amount in currency units")
    st.markdown("- `ProductCD`: product category code (W/H/C/S/R)")
    st.markdown("- `card1`: primary card identifier")

    with st.form("single_prediction"):
        col1, col2, col3 = st.columns(3)
        transaction_amt = col1.number_input("TransactionAmt", min_value=0.0, value=120.5)
        product_cd = col2.selectbox("ProductCD", options=["W", "H", "C", "S", "R"], index=0)
        card1 = col3.number_input("card1", min_value=0, value=1000, step=1)

        with st.expander("Optional card fields"):
            o1, o2, o3 = st.columns(3)
            card2 = o1.number_input("card2", min_value=0.0, value=0.0)
            card3 = o2.number_input("card3", min_value=0.0, value=0.0)
            card4 = o3.text_input("card4", value="visa")
            o4, o5, o6 = st.columns(3)
            card5 = o4.number_input("card5", min_value=0.0, value=0.0)
            card6 = o5.text_input("card6", value="credit")
            include_optional = o6.checkbox("Include optional fields", value=False)

        submitted = st.form_submit_button("Predict Risk")

    if submitted:
        transaction = {
            "TransactionAmt": transaction_amt,
            "ProductCD": product_cd,
            "card1": int(card1),
        }
        if include_optional:
            transaction.update(
                {
                    "card2": card2,
                    "card3": card3,
                    "card4": card4,
                    "card5": card5,
                    "card6": card6,
                }
            )

        prediction = predict_one(transaction)
        if "error" in prediction:
            st.error(f"Prediction failed: {prediction['error']}")
        else:
            risk_score = float(prediction.get("risk_score", 0.0))
            raw_label = int(prediction.get("predicted_label", 0))
            severity = str(prediction.get("severity", "low")).lower()
            label_text = "Fraud" if raw_label == 1 else "Not Fraud"

            p1, p2, p3 = st.columns(3)
            p1.metric("Risk Score", f"{risk_score:.4f}")
            p2.metric("Predicted Label", label_text)
            p3.metric("Severity", severity.upper())

            if severity in {"low", "medium"}:
                st.warning(f"Interpretation: transaction is {severity} risk; review based on policy.")
            elif severity in {"high", "critical"}:
                st.error(f"Interpretation: transaction is {severity} risk; prioritize manual review.")
            else:
                st.info("Interpretation: prediction completed, severity was not recognized.")

with st.container(border=True):
    st.subheader("Batch Prediction (Optional)")
    st.caption("Send multiple transactions to `POST /predict/batch` as a JSON list.")
    sample_payload = [
        {"TransactionAmt": 120.5, "ProductCD": "W", "card1": 1000},
        {"TransactionAmt": 5.0, "ProductCD": "H", "card1": 2345},
    ]
    batch_input = st.text_area(
        "Paste JSON list of transactions",
        value=json.dumps(sample_payload, indent=2),
        height=180,
    )
    if st.button("Run Batch Prediction"):
        try:
            transactions = json.loads(batch_input)
            if not isinstance(transactions, list):
                raise ValueError("Input must be a JSON list.")
        except (json.JSONDecodeError, ValueError) as exc:
            st.error(f"Invalid JSON input: {exc}")
        else:
            batch = predict_batch(transactions)
            if "error" in batch:
                st.error(f"Batch prediction failed: {batch['error']}")
            else:
                st.dataframe(batch.get("predictions", []), width="stretch", hide_index=True)

with st.container(border=True):
    st.subheader("Alerts")
    if alerts_error is not None:
        st.warning("Alerts unavailable because API is down or alert endpoint is unreachable.")
        st.caption(f"Error detail: {alerts_error}")
    else:
        st.caption(f"Recent alerts loaded: {len(alerts)}")
        if alerts:
            st.dataframe(
                [
                    {
                        "severity": item.get("severity"),
                        "risk_score": item.get("risk_score"),
                        "predicted_label": item.get("predicted_label"),
                        "reason_codes": ", ".join(item.get("reason_codes", [])),
                        "recommended_action": item.get("recommended_action"),
                        "timestamp": item.get("timestamp"),
                    }
                    for item in alerts
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            st.info("No alerts yet. Generate one from the sample transaction to populate this panel.")

    if st.button("Generate Alert From Sample Transaction"):
        sample_transaction = {"TransactionAmt": 120.5, "ProductCD": "W", "card1": 1000}
        alert = evaluate_alert(sample_transaction)
        if "error" in alert:
            st.warning(f"Could not evaluate alert: {alert['error']}")
        else:
            st.success(f"Alert generated: {alert.get('alert_id')}")
            st.json(alert)

with st.container(border=True):
    st.subheader("Model Metrics")
    metrics_report = load_json_report(METRICS_PATH)
    if metrics_report is None:
        st.warning(f"Missing or invalid metrics report: {METRICS_PATH}")
    else:
        core_metrics = extract_core_metrics(metrics_report)
        cols = st.columns(6)
        for idx, key in enumerate(["precision", "recall", "f1", "roc_auc", "pr_auc", "threshold"]):
            value = core_metrics.get(key)
            cols[idx].metric(key, f"{value:.4f}" if value is not None else "n/a")

        st.caption("Recall matters for catching more fraud cases.")
        st.caption("Precision matters for reducing false positives and review load.")
        st.caption("PR-AUC is especially useful for imbalanced fraud detection problems.")
        render_metrics_chart(core_metrics)

with st.container(border=True):
    st.subheader("Threshold Report")
    st.caption("Threshold selection trades off recall against alert volume and review capacity.")
    threshold_report = load_json_report(THRESHOLD_PATH)
    if threshold_report is None:
        st.warning(f"Missing or invalid threshold report: {THRESHOLD_PATH}")
    else:
        threshold_rows = threshold_report.get("threshold_rows", [])
        render_threshold_rows(threshold_rows)
