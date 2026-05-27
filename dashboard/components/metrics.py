"""Metric/report loading helpers for dashboard rendering."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

METRICS_KEYS = ["precision", "recall", "f1", "roc_auc", "pr_auc", "threshold"]


def load_json_report(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def extract_core_metrics(metrics_report: dict[str, Any]) -> dict[str, float | None]:
    return {
        key: float(metrics_report[key]) if key in metrics_report else None
        for key in METRICS_KEYS
    }
