"""Evaluation utilities for fraud baseline models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def evaluate_classification(
    y_true: pd.Series,
    y_pred: np.ndarray,
    y_score: np.ndarray,
) -> dict[str, Any]:
    """Compute fraud-focused metrics for binary classification."""
    metrics = {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_score)),
        "pr_auc": float(average_precision_score(y_true, y_score)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    return metrics


def save_metrics(metrics: dict[str, Any], config: dict[str, Any]) -> Path:
    """Save metrics report to configured report path."""
    metrics_path = Path(config["artifacts"]["metrics_file"])
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    logger.info(f"Saved metrics to {metrics_path}")
    return metrics_path


def build_threshold_report(
    y_true: pd.Series,
    y_score: np.ndarray,
    *,
    fixed_thresholds: list[float] | None = None,
    topk_percents: list[float] | None = None,
) -> dict[str, Any]:
    """Create operational threshold table for alerting capacity decisions."""
    fixed_thresholds = fixed_thresholds or [0.2, 0.5, 0.8, 0.95]
    topk_percents = topk_percents or [1.0, 0.5, 0.1]
    total = len(y_true)

    def _row_from_threshold(label: str, threshold: float) -> dict[str, Any]:
        y_pred = (y_score >= threshold).astype(int)
        alerts = int(y_pred.sum())
        return {
            "label": label,
            "threshold": float(threshold),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "alerts": alerts,
            "alerts_per_10k": float((alerts / total) * 10000),
        }

    rows: list[dict[str, Any]] = []
    for threshold in fixed_thresholds:
        rows.append(_row_from_threshold(f"fixed_{threshold}", threshold))

    sorted_scores = np.sort(y_score)
    for pct in topk_percents:
        top_n = max(1, int(np.ceil(total * (pct / 100.0))))
        threshold = float(sorted_scores[-top_n])
        rows.append(_row_from_threshold(f"top_{pct}_pct", threshold))

    pr_precision, pr_recall, pr_thresholds = precision_recall_curve(y_true, y_score)
    return {
        "n_samples": total,
        "threshold_rows": rows,
        "pr_curve_summary": {
            "points": int(len(pr_precision)),
            "max_precision": float(np.max(pr_precision)),
            "max_recall": float(np.max(pr_recall)),
            "threshold_min": float(np.min(pr_thresholds)) if len(pr_thresholds) else None,
            "threshold_max": float(np.max(pr_thresholds)) if len(pr_thresholds) else None,
        },
        "recommended_threshold_note": "choose based on review capacity and business cost tradeoffs",
    }


def save_threshold_report(report: dict[str, Any], config: dict[str, Any]) -> Path:
    """Persist threshold report to reports directory."""
    reports_dir = Path(config["artifacts"]["reports_dir"])
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / "threshold_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    logger.info("Saved threshold report to %s", output_path)
    return output_path
