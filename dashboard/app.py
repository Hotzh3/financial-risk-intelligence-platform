"""Streamlit dashboard for Financial Risk Intelligence Platform (Phase 4)."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from dashboard.components.charts import render_metrics_chart, render_threshold_rows
from dashboard.components.metrics import extract_core_metrics, load_json_report
from dashboard.utils.api_client import (
    get_api_base_url,
    get_health,
    get_model_metadata,
    predict_batch,
    predict_one,
)

REPORTS_DIR = Path("reports")
METRICS_PATH = REPORTS_DIR / "model_metrics.json"
THRESHOLD_PATH = REPORTS_DIR / "threshold_report.json"
SEVERITY_COLORS = {
    "low": "#2e7d32",
    "medium": "#f9a825",
    "high": "#ef6c00",
    "critical": "#c62828",
}


st.set_page_config(page_title="Financial Risk Intelligence Platform", layout="wide")
st.title("Financial Risk Intelligence Platform")
st.caption("Fraud-risk monitoring dashboard for API health, model quality, and live scoring.")

api_base_url = get_api_base_url()

with st.container(border=True):
    st.subheader("API Health")
    health = get_health()
    if "error" in health:
        st.warning(
            "API unavailable. Start it with: `python -m uvicorn src.api.main:app --reload`"
        )
        st.caption(f"Configured API_BASE_URL: {api_base_url}")
    else:
        st.success(f"Status: {health.get('status', 'unknown')}")
        st.caption(f"Service: {health.get('service', 'n/a')} | API_BASE_URL: {api_base_url}")

with st.container(border=True):
    st.subheader("Model Metadata")
    metadata = get_model_metadata()
    if "error" in metadata:
        st.warning(f"Could not load model metadata: {metadata['error']}")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Model", metadata.get("model_name") or "n/a")
        c2.metric("Target", metadata.get("target_column") or "n/a")
        c3.metric("Features", metadata.get("number_of_features") or "n/a")
        c4.metric("Threshold", metadata.get("threshold") or "n/a")
        artifacts = metadata.get("artifacts", {})
        artifact_rows = []
        for name, item in artifacts.items():
            artifact_rows.append(
                {
                    "artifact": name,
                    "path": item.get("path", "n/a"),
                    "exists": item.get("exists", False),
                }
            )
        if artifact_rows:
            st.dataframe(artifact_rows, use_container_width=True, hide_index=True)

with st.container(border=True):
    st.subheader("Single Prediction")
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
            severity = str(prediction.get("severity", "low")).lower()
            color = SEVERITY_COLORS.get(severity, "#424242")
            st.markdown(
                f"<div style='padding:10px;border-radius:8px;background-color:{color};color:white;font-weight:600;'>"
                f"Severity: {severity.upper()}</div>",
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns(2)
            c1.metric("Risk Score", f"{float(prediction.get('risk_score', 0.0)):.4f}")
            c2.metric("Predicted Label", str(prediction.get("predicted_label", "n/a")))

with st.container(border=True):
    st.subheader("Batch Prediction (Optional)")
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
                st.dataframe(batch.get("predictions", []), use_container_width=True, hide_index=True)

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
        render_metrics_chart(core_metrics)

with st.container(border=True):
    st.subheader("Threshold Report")
    threshold_report = load_json_report(THRESHOLD_PATH)
    if threshold_report is None:
        st.warning(f"Missing or invalid threshold report: {THRESHOLD_PATH}")
    else:
        threshold_rows = threshold_report.get("threshold_rows", [])
        render_threshold_rows(threshold_rows)
