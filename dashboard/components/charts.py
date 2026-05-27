"""Chart/table rendering helpers for dashboard."""

from __future__ import annotations

import pandas as pd
import streamlit as st


METRIC_CHART_KEYS = ["precision", "recall", "f1", "roc_auc", "pr_auc"]


def render_metrics_chart(core_metrics: dict[str, float | None]) -> None:
    rows = [{"metric": k, "value": v} for k, v in core_metrics.items() if k in METRIC_CHART_KEYS and v is not None]
    if not rows:
        st.info("No metric values available for charting.")
        return
    frame = pd.DataFrame(rows).set_index("metric")
    st.bar_chart(frame)


def render_threshold_rows(threshold_rows: list[dict]) -> None:
    if not threshold_rows:
        st.info("No threshold rows available.")
        return
    frame = pd.DataFrame(threshold_rows)
    preferred_columns = [
        "label",
        "threshold",
        "precision",
        "recall",
        "alerts",
        "alerts_per_10k",
    ]
    columns = [col for col in preferred_columns if col in frame.columns]
    st.dataframe(frame[columns] if columns else frame, use_container_width=True, hide_index=True)
