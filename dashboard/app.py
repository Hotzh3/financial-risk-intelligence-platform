"""
Streamlit Dashboard for the Financial Risk Intelligence Platform.
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Financial Risk Intelligence Platform",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Financial Risk Intelligence Platform")
st.markdown("Real-time fraud detection dashboard")

# ── KPIs ──────────────────────────────────────────────────────────────
st.header("System Metrics")

try:
    response = requests.get(f"{API_URL}/api/v1/metrics", timeout=3)
    metrics = response.json()
    api_status = "🟢 Online"
except Exception:
    metrics = {
        "total_transactions": 590540,
        "fraud_rate": 0.035,
        "roc_auc": 0.7120,
        "model": "Isolation Forest"
    }
    api_status = "🔴 Offline"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("API Status", api_status)
col2.metric("Total Transactions", f"{metrics['total_transactions']:,}")
col3.metric("Fraud Rate", f"{metrics['fraud_rate']*100:.1f}%")
col4.metric("ROC-AUC", f"{metrics['roc_auc']:.4f}")
col5.metric("Model", metrics['model'])

st.divider()

# ── Fraud Distribution ────────────────────────────────────────────────
st.header("Fraud Distribution")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(6, 4))
    labels = ['Legitimate', 'Fraud']
    sizes = [1 - metrics['fraud_rate'], metrics['fraud_rate']]
    colors = ['#2ecc71', '#e74c3c']
    ax.pie(sizes, labels=labels, colors=colors,
           autopct='%1.1f%%', startangle=90,
           wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    ax.set_title('Class Distribution')
    st.pyplot(fig)

with col2:
    fraud_count = int(metrics['total_transactions'] * metrics['fraud_rate'])
    legit_count = metrics['total_transactions'] - fraud_count
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(['Legitimate', 'Fraud'], [legit_count, fraud_count],
           color=['#2ecc71', '#e74c3c'])
    ax.set_title('Transaction Count by Class')
    ax.set_ylabel('Count')
    for i, v in enumerate([legit_count, fraud_count]):
        ax.text(i, v + 1000, f'{v:,}', ha='center', fontweight='bold')
    st.pyplot(fig)

st.divider()

# ── Alerts Panel ────────────────────────────────────────────────────────
st.header("🚨 Alerts Panel")

alerts_stats = None
alerts_rows = []

if st.button("Refresh Alerts", use_container_width=False):
    st.rerun()

try:
    stats_response = requests.get(f"{API_URL}/api/v1/alerts/stats", timeout=3)
    stats_response.raise_for_status()
    alerts_stats = stats_response.json()

    alerts_response = requests.get(f"{API_URL}/api/v1/alerts?limit=20", timeout=3)
    alerts_response.raise_for_status()
    alerts_rows = alerts_response.json().get("alerts", [])
except Exception:
    st.info("Alerts service not available yet. Showing fraud dashboard without alerts.")

if alerts_stats is not None:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Alerts", alerts_stats.get("total_alerts", 0))
    m2.metric("Low", alerts_stats.get("low", 0))
    m3.metric("Medium", alerts_stats.get("medium", 0))
    m4.metric("High", alerts_stats.get("high", 0))
    m5.metric("Notified %", f"{alerts_stats.get('notified_pct', 0.0):.1f}%")

    with st.expander("Threshold Configuration"):
        current_threshold = st.slider(
            "Alert threshold",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            value=0.70,
        )
        if st.button("Update threshold", key="update_threshold_btn"):
            try:
                update_res = requests.patch(
                    f"{API_URL}/api/v1/alerts/threshold",
                    json={"threshold": current_threshold},
                    timeout=3,
                )
                update_res.raise_for_status()
                st.success(f"Threshold updated to {update_res.json()['threshold']:.2f}")
            except Exception as exc:
                st.warning(f"Could not update threshold: {exc}")

    if alerts_rows:
        alerts_df = pd.DataFrame(alerts_rows)
        alerts_df["severity_color"] = alerts_df["severity"].map(
            {"LOW": "🟢 LOW", "MEDIUM": "🟡 MEDIUM", "HIGH": "🔴 HIGH"}
        ).fillna(alerts_df["severity"])
        display_columns = [
            "timestamp",
            "transaction_id",
            "anomaly_score",
            "severity_color",
            "risk_level",
            "amount",
            "status",
        ]
        st.dataframe(alerts_df[display_columns], use_container_width=True, hide_index=True)
    else:
        st.caption("No alerts generated yet.")

st.divider()

# ── Live Prediction ───────────────────────────────────────────────────
st.header("🔍 Live Transaction Scoring")

with st.form("predict_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        amount = st.number_input("Transaction Amount ($)", min_value=0.0, value=100.0)
        hour = st.slider("Hour of Day", 0, 23, 14)
        product = st.selectbox("Product Category", [0, 1, 2, 3, 4])

    with col2:
        card1 = st.number_input("Card 1", value=1234)
        card2 = st.number_input("Card 2", value=111.0)
        card3 = st.number_input("Card 3", value=150.0)

    with col3:
        v45 = st.number_input("V45", value=1.0)
        v86 = st.number_input("V86", value=1.0)
        v87 = st.number_input("V87", value=1.0)

    submitted = st.form_submit_button("Score Transaction")

if submitted:
    payload = {
        "TransactionAmt": amount,
        "ProductCD": product,
        "card1": int(card1),
        "card2": card2,
        "card3": card3,
        "card5": 226.0,
        "card4": 1,
        "card6": 1,
        "hour": hour,
        "V45": v45,
        "V86": v86,
        "V87": v87,
        "V44": 1.0,
        "V52": 1.0,
    }

    try:
        res = requests.post(f"{API_URL}/api/v1/predict", json=payload, timeout=5)
        result = res.json()

        risk = result['risk_level']
        score = result['anomaly_score']

        if risk == "HIGH":
            st.error(f"🚨 HIGH RISK — Anomaly Score: {score:.4f}")
        elif risk == "MEDIUM":
            st.warning(f"⚠️ MEDIUM RISK — Anomaly Score: {score:.4f}")
        else:
            st.success(f"✅ LOW RISK — Anomaly Score: {score:.4f}")

        st.json(result)

    except Exception as e:
        st.error(f"API Error: {e}")