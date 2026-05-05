"""Train Phase 2 baseline fraud models."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from src.models.evaluate import evaluate_classification, save_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_CONFIG_PATH = Path("config/config.yaml")


def load_config(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def load_features(config: dict[str, Any]) -> tuple[pd.DataFrame, pd.Series, str]:
    features_path = Path(config["data"]["processed_files"]["features"])
    if not features_path.exists():
        raise FileNotFoundError(
            f"Features file not found: {features_path}. Run `python3 -m src.features.build_features`."
        )

    df = pd.read_csv(features_path)
    target_candidates = config["schema"]["possible_target_columns"]
    target_col = next((col for col in target_candidates if col in df.columns), None)
    if not target_col:
        raise ValueError(f"No target found in features file. Tried {target_candidates}")

    X = df.drop(columns=[target_col]).copy()
    y = df[target_col].astype(int).copy()
    return X, y, target_col


def get_baseline_model(config: dict[str, Any]) -> LogisticRegression | RandomForestClassifier:
    model_name = config["modeling"]["baseline_model"]["name"]
    random_state = config["project"]["random_state"]
    if model_name == "logistic_regression":
        params = dict(config["modeling"]["baseline_model"]["params"])
        params["random_state"] = random_state
        return LogisticRegression(**params)
    if model_name == "random_forest":
        params = dict(config["modeling"]["random_forest"]["params"])
        params["random_state"] = random_state
        return RandomForestClassifier(**params)
    raise ValueError(f"Unsupported baseline model: {model_name}")


def save_pickle(obj: Any, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as file:
        pickle.dump(obj, file)
    return path


def run_training(config_path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Train baseline model and save model artifacts + evaluation report."""
    config = load_config(config_path)
    X, y, target_col = load_features(config)

    test_size = config["processing"]["test_size"]
    random_state = config["processing"]["random_state"]
    stratify_target = y if config["processing"]["stratify"] else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=stratify_target,
    )

    model = get_baseline_model(config)
    model.fit(X_train, y_train)

    threshold = float(config["evaluation"]["threshold"]["default"])
    y_score = model.predict_proba(X_test)[:, 1]
    y_pred = (y_score >= threshold).astype(int)

    metrics = evaluate_classification(y_test, y_pred, y_score)
    metrics.update(
        {
            "model_name": config["modeling"]["baseline_model"]["name"],
            "target_column": target_col,
            "threshold": threshold,
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
        }
    )
    save_metrics(metrics, config)

    model_path = Path(config["artifacts"]["model_file"])
    save_pickle(model, model_path)

    if config["modeling"]["anomaly_model"]["enabled"]:
        iso_params = config["modeling"]["anomaly_model"]["params"]
        iso_model = IsolationForest(**iso_params)
        iso_model.fit(X_train)
        iso_path = Path(config["artifacts"]["models_dir"]) / "isolation_forest.pkl"
        save_pickle(iso_model, iso_path)
        metrics["isolation_forest_path"] = str(iso_path)

    print(f"Trained baseline model: {metrics['model_name']}")
    print(f"Train shape: {X_train.shape} | Test shape: {X_test.shape}")
    print(f"Saved model: {model_path}")
    print(f"Saved metrics: {config['artifacts']['metrics_file']}")
    return metrics


if __name__ == "__main__":
    run_training()