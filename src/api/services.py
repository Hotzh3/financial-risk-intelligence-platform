"""Service layer for model metadata and prediction endpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.models.predict import predict_risk

DEFAULT_CONFIG_PATH = Path("config/config.yaml")


class PredictionService:
    """Reads config/artifacts and exposes prediction helpers for API routes."""

    def __init__(self, config_path: str | Path = DEFAULT_CONFIG_PATH) -> None:
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    @property
    def artifacts_paths(self) -> dict[str, Path]:
        models_dir = Path(self.config["artifacts"]["models_dir"])
        return {
            "model_file": Path(self.config["artifacts"]["model_file"]),
            "feature_columns": models_dir / "feature_columns.json",
            "run_metadata": models_dir / "run_metadata.json",
            "metrics": Path(self.config["artifacts"]["metrics_file"]),
        }

    def _load_json_if_exists(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def get_model_metadata(self) -> dict[str, Any]:
        paths = self.artifacts_paths
        artifacts = {
            name: {"path": str(path), "exists": path.exists()} for name, path in paths.items()
        }
        run_metadata = self._load_json_if_exists(paths["run_metadata"]) or {}
        metrics = self._load_json_if_exists(paths["metrics"]) or {}

        return {
            "model_name": metrics.get("model_name"),
            "target_column": run_metadata.get("target_column"),
            "number_of_features": run_metadata.get("feature_columns_count"),
            "threshold": float(self.config["evaluation"]["threshold"]["default"]),
            "artifacts": artifacts,
        }

    def _severity_from_score(self, score: float) -> str:
        thresholds = self.config.get("alerts", {}).get("severity_thresholds", {})
        low = float(thresholds.get("low", 0.2))
        medium = float(thresholds.get("medium", 0.5))
        high = float(thresholds.get("high", 0.8))
        critical = float(thresholds.get("critical", 0.95))
        if score >= critical:
            return "critical"
        if score >= high:
            return "high"
        if score >= medium:
            return "medium"
        if score >= low:
            return "low"
        return "low"

    def predict_one(self, transaction: dict[str, Any]) -> dict[str, Any]:
        frame = pd.DataFrame([transaction])
        result = predict_risk(frame, config_path=self.config_path).iloc[0]
        risk_score = float(result["risk_score"])
        return {
            "risk_score": risk_score,
            "predicted_label": int(result["predicted_label"]),
            "severity": self._severity_from_score(risk_score),
        }

    def predict_batch(self, transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not transactions:
            return []
        frame = pd.DataFrame(transactions)
        predictions = predict_risk(frame, config_path=self.config_path)
        output: list[dict[str, Any]] = []
        for _, row in predictions.iterrows():
            risk_score = float(row["risk_score"])
            output.append(
                {
                    "risk_score": risk_score,
                    "predicted_label": int(row["predicted_label"]),
                    "severity": self._severity_from_score(risk_score),
                }
            )
        return output

