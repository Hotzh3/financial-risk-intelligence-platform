"""Build reproducible modeling features for Phase 2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Load YAML config."""
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def detect_target_column(df: pd.DataFrame, config: dict[str, Any]) -> str:
    """Detect target column using configured candidates."""
    candidates = config["schema"]["possible_target_columns"]
    target_col = next((column for column in candidates if column in df.columns), None)
    if not target_col:
        raise ValueError(f"No target column found. Tried: {candidates}")
    return target_col


def load_clean_data(config: dict[str, Any]) -> pd.DataFrame:
    """Load cleaned data from configured path."""
    clean_path = Path(config["data"]["processed_files"]["clean_transactions"])
    if not clean_path.exists():
        raise FileNotFoundError(
            f"Clean data not found at '{clean_path}'. Run `python3 -m src.data.clean_data` first."
        )
    return pd.read_csv(clean_path)


def _is_low_cardinality(series: pd.Series, max_cardinality: int = 30) -> bool:
    return series.nunique(dropna=True) <= max_cardinality


def build_features(df: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, str]:
    """
    Build deterministic feature table.

    Leakage prevention:
    - Drops configured identifier columns (for example `TransactionID`)
    - Never uses target-derived aggregations
    """
    target_col = detect_target_column(df, config)
    leakage_columns = set(config["features"].get("leakage_columns", []))
    drop_columns = set(config["processing"].get("drop_columns", []))
    excluded = leakage_columns.union(drop_columns).union({target_col})

    X = df.drop(columns=[col for col in excluded if col in df.columns]).copy()
    y = df[target_col].copy()

    for column in X.columns:
        if pd.api.types.is_numeric_dtype(X[column]):
            X[column] = pd.to_numeric(X[column], errors="coerce")
            X[column] = X[column].fillna(X[column].median())
        else:
            X[column] = X[column].astype(str).fillna("Unknown")

    categorical_columns = [
        column
        for column in X.select_dtypes(include=["object"]).columns
        if _is_low_cardinality(X[column], max_cardinality=30)
    ]
    high_cardinality_columns = [
        column
        for column in X.select_dtypes(include=["object"]).columns
        if column not in categorical_columns
    ]

    freq_encoded_columns: dict[str, pd.Series] = {}
    for column in high_cardinality_columns:
        freq_map = X[column].value_counts(normalize=True)
        freq_encoded_columns[f"{column}_freq"] = X[column].map(freq_map).fillna(0.0)

    if high_cardinality_columns:
        X = X.drop(columns=high_cardinality_columns)
        X = pd.concat([X, pd.DataFrame(freq_encoded_columns, index=X.index)], axis=1)

    X = pd.get_dummies(X, columns=categorical_columns, drop_first=False)
    X = X.fillna(0)

    features_df = X.copy()
    features_df[target_col] = y
    return features_df, target_col


def save_features(features_df: pd.DataFrame, target_col: str, config: dict[str, Any]) -> Path:
    """Save built features and artifact metadata."""
    features_path = Path(config["data"]["processed_files"]["features"])
    features_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(features_path, index=False)

    columns_artifact = Path(config["artifacts"]["models_dir"]) / "feature_columns.json"
    columns_artifact.parent.mkdir(parents=True, exist_ok=True)
    feature_columns = [column for column in features_df.columns if column != target_col]
    columns_artifact.write_text(
        json.dumps({"target_column": target_col, "feature_columns": feature_columns}, indent=2),
        encoding="utf-8",
    )

    logger.info(f"Saved feature table to {features_path}")
    logger.info(f"Saved feature metadata to {columns_artifact}")
    return features_path


def run_build_features(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Path:
    """Run end-to-end feature build."""
    config = load_config(config_path)
    clean_df = load_clean_data(config)
    features_df, target_col = build_features(clean_df, config)
    output_path = save_features(features_df, target_col, config)
    print(f"Input clean shape: {clean_df.shape}")
    print(f"Features shape: {features_df.shape}")
    print(f"Target column: {target_col}")
    print(f"Saved features: {output_path}")
    return output_path


if __name__ == "__main__":
    run_build_features()
