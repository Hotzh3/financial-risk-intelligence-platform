"""Build leak-safe modeling table for Phase 2/2.5."""

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


def build_features(df: pd.DataFrame, config: dict[str, Any]) -> tuple[pd.DataFrame, str, list[str]]:
    """
    Build deterministic, leak-safe feature table before model preprocessing.

    Leakage prevention:
    - Drops configured identifier columns (for example `TransactionID`)
    - Ensures target is removed from X
    """
    target_col = detect_target_column(df, config)
    leakage_columns = set(config["features"].get("leakage_columns", []))
    drop_columns = set(config["processing"].get("drop_columns", []))
    excluded = leakage_columns.union(drop_columns).union({target_col})

    X = df.drop(columns=[col for col in excluded if col in df.columns]).copy()
    y = df[target_col].copy()

    # Keep raw-ish columns here; train pipeline performs imputing/encoding/scaling.
    for column in X.select_dtypes(include=["object"]).columns:
        X[column] = X[column].astype("string")

    features_df = X.copy()
    features_df[target_col] = pd.to_numeric(y, errors="coerce")
    features_df = features_df.dropna(subset=[target_col]).copy()
    features_df[target_col] = features_df[target_col].astype(int)
    return features_df, target_col, sorted(excluded)


def save_features(
    features_df: pd.DataFrame,
    target_col: str,
    excluded_columns: list[str],
    config: dict[str, Any],
) -> Path:
    """Save built features and artifact metadata."""
    features_path = Path(config["data"]["processed_files"]["features"])
    features_path.parent.mkdir(parents=True, exist_ok=True)
    features_df.to_csv(features_path, index=False)

    columns_artifact = Path(config["artifacts"]["models_dir"]) / "feature_columns.json"
    columns_artifact.parent.mkdir(parents=True, exist_ok=True)
    feature_columns = [column for column in features_df.columns if column != target_col]
    columns_artifact.write_text(
        json.dumps(
            {
                "target_column": target_col,
                "feature_columns": feature_columns,
                "excluded_columns": excluded_columns,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.info(f"Saved feature table to {features_path}")
    logger.info(f"Saved feature metadata to {columns_artifact}")
    return features_path


def run_build_features(config_path: str | Path = DEFAULT_CONFIG_PATH) -> Path:
    """Run end-to-end feature build."""
    config = load_config(config_path)
    clean_df = load_clean_data(config)
    features_df, target_col, excluded_columns = build_features(clean_df, config)
    output_path = save_features(features_df, target_col, excluded_columns, config)
    print(f"Input clean shape: {clean_df.shape}")
    print(f"Features shape: {features_df.shape}")
    print(f"Target column: {target_col}")
    print(f"Excluded columns (anti-leakage): {excluded_columns}")
    print(f"Saved features: {output_path}")
    return output_path


if __name__ == "__main__":
    run_build_features()
