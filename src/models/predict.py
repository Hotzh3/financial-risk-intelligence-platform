"""Inference utilities for Phase 2 baseline model."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)
DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def _load_model(model_path: str | Path) -> Any:
    with open(model_path, "rb") as file:
        return pickle.load(file)


def _load_feature_columns(path: str | Path) -> list[str]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return payload["feature_columns"]


def _load_run_metadata(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _ensure_artifacts_exist(*paths: str | Path) -> None:
    missing = [str(path) for path in paths if not Path(path).exists()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing required artifacts: {missing_list}. "
            "Run `python3 -m src.models.train` after building features."
        )


def _prepare_input(data: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Align incoming dataframe to training feature schema before pipeline transform."""
    aligned = data.copy()
    missing_columns = [column for column in feature_columns if column not in aligned.columns]
    if missing_columns:
        missing_df = pd.DataFrame(np.nan, index=aligned.index, columns=missing_columns)
        aligned = pd.concat([aligned, missing_df], axis=1)
    aligned = aligned.reindex(columns=feature_columns)
    return aligned


def _prepare_legacy_input(data: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Backwards-compatible path for older non-pipeline saved models."""
    transformed = pd.get_dummies(data.copy(), drop_first=False)
    transformed = transformed.reindex(columns=feature_columns, fill_value=0)
    return transformed


def predict_risk(
    data: pd.DataFrame,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> pd.DataFrame:
    """Return risk score and predicted label for incoming rows."""
    config = load_config(config_path)
    model_path = Path(config["artifacts"]["model_file"])
    feature_columns_path = Path(config["artifacts"]["models_dir"]) / "feature_columns.json"
    run_metadata_path = Path(config["artifacts"]["models_dir"]) / "run_metadata.json"
    _ensure_artifacts_exist(model_path, feature_columns_path, run_metadata_path)

    model = _load_model(model_path)
    feature_columns = _load_feature_columns(feature_columns_path)
    run_metadata = _load_run_metadata(run_metadata_path)
    metadata_feature_columns = run_metadata.get("feature_columns", [])
    if feature_columns != metadata_feature_columns:
        raise RuntimeError(
            "Artifact mismatch: feature_columns.json does not match run_metadata.json. "
            "Re-run `python3 -m src.models.train` to regenerate consistent artifacts."
        )

    threshold = float(config["evaluation"]["threshold"]["default"])

    if hasattr(model, "named_steps") and "preprocessor" in model.named_steps:
        X = _prepare_input(data, feature_columns=feature_columns)
    else:
        X = _prepare_legacy_input(data, feature_columns=feature_columns)
    try:
        risk_scores = model.predict_proba(X)[:, 1]
    except ValueError as error:
        raise RuntimeError(
            "Loaded model is incompatible with current feature metadata. "
            "Re-run `python3 -m src.models.train` after rebuilding features."
        ) from error
    predicted_label = (risk_scores >= threshold).astype(int)

    output = data.copy()
    output["risk_score"] = risk_scores
    output["predicted_label"] = predicted_label
    return output


if __name__ == "__main__":
    sample = pd.DataFrame(
        [
            {
                "TransactionAmt": 120.5,
                "ProductCD": "W",
                "card1": 1000,
            }
        ]
    )
    predictions = predict_risk(sample)
    print(predictions[["risk_score", "predicted_label"]])
