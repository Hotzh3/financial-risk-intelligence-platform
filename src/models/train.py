"""
Model training for the Financial Risk Intelligence Platform.
Isolation Forest for anomaly detection with MLflow tracking.
"""

import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import pickle
from pathlib import Path
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)
from src.utils.logger import get_logger
from src.features.engineering import run_feature_engineering

logger = get_logger(__name__)


def load_clean_data() -> pd.DataFrame:
    return pd.read_parquet("data/processed/train_clean.parquet")


def train_model(X_train: pd.DataFrame, contamination: float = 0.035) -> IsolationForest:
    """Train Isolation Forest model."""
    logger.info(f"Training Isolation Forest — contamination: {contamination}")
    model = IsolationForest(
        contamination=contamination,
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train)
    logger.info("Model trained successfully")
    return model


def evaluate_model(
    model: IsolationForest,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> dict:
    """Evaluate model and return metrics."""
    # Isolation Forest: -1 = anomaly, 1 = normal
    raw_preds = model.predict(X_test)
    y_pred = (raw_preds == -1).astype(int)

    # Anomaly scores (lower = more anomalous)
    scores = model.decision_function(X_test)
    anomaly_scores = -scores  # flip so higher = more suspicious

    metrics = {
        "roc_auc": roc_auc_score(y_test, anomaly_scores),
        "avg_precision": average_precision_score(y_test, anomaly_scores),
        "precision": classification_report(y_test, y_pred, output_dict=True)['1']['precision'],
        "recall": classification_report(y_test, y_pred, output_dict=True)['1']['recall'],
        "f1": classification_report(y_test, y_pred, output_dict=True)['1']['f1-score'],
    }

    logger.info(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    logger.info(f"Avg Precision: {metrics['avg_precision']:.4f}")
    logger.info(f"Precision: {metrics['precision']:.4f}")
    logger.info(f"Recall: {metrics['recall']:.4f}")
    logger.info(f"F1: {metrics['f1']:.4f}")

    return metrics


def save_model(model: IsolationForest, path: str = "models/isolation_forest.pkl") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {path}")


if __name__ == "__main__":
    mlflow.set_experiment("fraud-detection")

    with mlflow.start_run(run_name="isolation-forest-baseline"):
        logger.info("=== Starting Model Training ===")

        df = load_clean_data()
        X, y = run_feature_engineering(df)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        logger.info(f"Train: {X_train.shape} | Test: {X_test.shape}")

        contamination = 0.035
        mlflow.log_param("contamination", contamination)
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("n_features", X_train.shape[1])

        model = train_model(X_train, contamination=contamination)

        metrics = evaluate_model(model, X_test, y_test)
        mlflow.log_metrics(metrics)

        mlflow.sklearn.log_model(model, "isolation_forest")
        save_model(model)

        print("\n=== RESULTS ===")
        for k, v in metrics.items():
            print(f"{k:<20} {v:.4f}")