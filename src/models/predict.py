"""Inference utilities for Phase 2 baseline model."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

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


def _prepare_input(data: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    processed = data.copy()

    for column in processed.columns:
        if pd.api.types.is_numeric_dtype(processed[column]):
            processed[column] = pd.to_numeric(processed[column], errors="coerce").fillna(0)
        else:
            processed[column] = processed[column].astype(str).fillna("Unknown")

    processed = pd.get_dummies(processed, drop_first=False)
    aligned = processed.reindex(columns=feature_columns, fill_value=0)
    return aligned


def predict_risk(
    data: pd.DataFrame,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> pd.DataFrame:
    """Return risk score and predicted label for incoming rows."""
    config = load_config(config_path)
    model = _load_model(config["artifacts"]["model_file"])
    feature_columns = _load_feature_columns(
        Path(config["artifacts"]["models_dir"]) / "feature_columns.json"
    )
    threshold = float(config["evaluation"]["threshold"]["default"])

    X = _prepare_input(data, feature_columns=feature_columns)
    risk_scores = model.predict_proba(X)[:, 1]
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
