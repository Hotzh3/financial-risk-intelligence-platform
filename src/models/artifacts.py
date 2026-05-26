"""Artifact metadata helpers for reproducible train/predict workflows."""

from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import sklearn


def compute_file_sha256(path: str | Path) -> str:
    """Return SHA256 digest for a file path."""
    file_path = Path(path)
    digest = hashlib.sha256()
    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_fingerprint(payload: dict[str, Any]) -> str:
    """Return deterministic SHA256 for JSON-serializable dict."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def build_run_metadata(
    *,
    config_path: str | Path,
    features_path: str | Path,
    target_column: str,
    feature_columns: list[str],
    n_rows_total: int,
    n_train: int,
    n_test: int,
    fraud_rate_full: float,
    fraud_rate_train: float,
    fraud_rate_test: float,
    sample_size_config: int | None,
    sample_size_effective: int | None,
    split_strategy: str,
) -> dict[str, Any]:
    """Build structured metadata describing a training run and its artifacts."""
    return {
        "run_id": datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ"),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config_path": str(config_path),
        "config_sha256": compute_file_sha256(config_path),
        "features_path": str(features_path),
        "features_sha256": compute_file_sha256(features_path),
        "target_column": target_column,
        "feature_columns": feature_columns,
        "feature_columns_count": len(feature_columns),
        "n_rows_total": int(n_rows_total),
        "n_train": int(n_train),
        "n_test": int(n_test),
        "fraud_rate_full": float(fraud_rate_full),
        "fraud_rate_train": float(fraud_rate_train),
        "fraud_rate_test": float(fraud_rate_test),
        "sample_size_config": sample_size_config,
        "sample_size_effective": sample_size_effective,
        "split_strategy": split_strategy,
        "python_version": platform.python_version(),
        "sklearn_version": sklearn.__version__,
    }
