"""Train Phase 2 baseline fraud models."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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


def maybe_stratified_sample(
    X: pd.DataFrame,
    y: pd.Series,
    config: dict[str, Any],
) -> tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    """
    Optionally subsample rows after loading features, stratified by target.
    When modeling.sample_size is null, returns X, y unchanged.
    """
    modeling_cfg = config.get("modeling", {})
    sample_size = modeling_cfg.get("sample_size")
    total_rows = len(X)
    meta: dict[str, Any] = {
        "training_data_mode": "full",
        "features_rows_before_sample": total_rows,
        "sample_size_config": sample_size,
    }

    if sample_size is None:
        logger.info(
            "Training on full feature set: %s rows (sample_size is null in config)",
            f"{total_rows:,}",
        )
        return X, y, meta

    n = int(sample_size)
    if n <= 0:
        raise ValueError(f"modeling.sample_size must be positive or null; got {sample_size!r}")

    if n >= total_rows:
        logger.warning(
            "modeling.sample_size (%s) >= loaded rows (%s); using full data",
            f"{n:,}",
            f"{total_rows:,}",
        )
        meta["training_data_mode"] = "full"
        meta["sample_size_effective"] = total_rows
        return X, y, meta

    random_state = config["processing"]["random_state"]
    # Always stratify subsampling by label when possible so fraud rate matches the full table.
    stratify_sample = y if y.nunique() > 1 else None
    fraud_rate_before = float(y.mean())

    X_sub, _, y_sub, _ = train_test_split(
        X,
        y,
        train_size=n,
        random_state=random_state,
        stratify=stratify_sample,
    )

    fraud_rate_after = float(y_sub.mean())
    meta["training_data_mode"] = "sampled"
    meta["sample_size_effective"] = int(len(X_sub))
    meta["fraud_rate_before_sample"] = fraud_rate_before
    meta["fraud_rate_after_sample"] = fraud_rate_after

    logger.info(
        "Training on stratified sample: %s rows (sample_size=%s from %s total; fraud rate %.4f -> %.4f)",
        f"{len(X_sub):,}",
        f"{n:,}",
        f"{total_rows:,}",
        fraud_rate_before,
        fraud_rate_after,
    )
    return X_sub, y_sub, meta


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


def build_preprocessor(X: pd.DataFrame, config: dict[str, Any]) -> ColumnTransformer:
    """Build reproducible preprocessing block shared by train and inference."""
    numeric_features = X.select_dtypes(include=["number", "bool"]).columns.tolist()
    categorical_features = X.select_dtypes(exclude=["number", "bool"]).columns.tolist()

    numeric_steps: list[tuple[str, Any]] = [
        ("imputer", SimpleImputer(strategy=config["processing"]["missing_values"]["numeric_strategy"]))
    ]
    if config["features"]["scaling"]["enabled"]:
        numeric_steps.append(("scaler", StandardScaler()))

    categorical_strategy = config["processing"]["missing_values"]["categorical_strategy"]
    categorical_steps: list[tuple[str, Any]] = [
        (
            "imputer",
            SimpleImputer(
                strategy="constant",
                fill_value=categorical_strategy,
            ),
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown=config["features"]["encoding"]["handle_unknown"],
            ),
        ),
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline(steps=numeric_steps), numeric_features),
            ("cat", Pipeline(steps=categorical_steps), categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


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
    X, y, sample_meta = maybe_stratified_sample(X, y, config)

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

    preprocessor = build_preprocessor(X_train, config)
    model = get_baseline_model(config)
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )
    pipeline.fit(X_train, y_train)

    threshold = float(config["evaluation"]["threshold"]["default"])
    y_score = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_score >= threshold).astype(int)

    metrics = evaluate_classification(y_test, y_pred, y_score)
    metrics.update(
        {
            "model_name": config["modeling"]["baseline_model"]["name"],
            "target_column": target_col,
            "threshold": threshold,
            "input_features": int(X_train.shape[1]),
            "n_train": int(len(X_train)),
            "n_test": int(len(X_test)),
            "train_shape": [int(X_train.shape[0]), int(X_train.shape[1])],
            "test_shape": [int(X_test.shape[0]), int(X_test.shape[1])],
            **sample_meta,
        }
    )
    save_metrics(metrics, config)

    model_path = Path(config["artifacts"]["model_file"])
    save_pickle(pipeline, model_path)
    save_pickle(preprocessor, Path(config["artifacts"]["preprocessor_file"]))

    if config["modeling"]["anomaly_model"]["enabled"]:
        iso_params = config["modeling"]["anomaly_model"]["params"]
        iso_model = IsolationForest(**iso_params)
        X_train_processed = preprocessor.transform(X_train)
        iso_model.fit(X_train_processed)
        iso_path = Path(config["artifacts"]["models_dir"]) / "isolation_forest.pkl"
        save_pickle(iso_model, iso_path)
        metrics["isolation_forest_path"] = str(iso_path)

    print(f"Trained baseline model: {metrics['model_name']}")
    print(
        f"Training data: {sample_meta['training_data_mode']} "
        f"(rows before any train/test split: {sample_meta['features_rows_before_sample']:,})"
    )
    if sample_meta["training_data_mode"] == "sampled":
        print(
            f"  Stratified sample effective size: {sample_meta['sample_size_effective']:,} "
            f"(config sample_size={sample_meta['sample_size_config']})"
        )
    print(f"Train shape: {X_train.shape} | Test shape: {X_test.shape}")
    print(f"Saved model: {model_path}")
    print(f"Saved preprocessor: {config['artifacts']['preprocessor_file']}")
    print(f"Saved metrics: {config['artifacts']['metrics_file']}")
    return metrics


if __name__ == "__main__":
    run_training()