"""Hardening tests for modeling reproducibility and guardrails."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from src.features.build_features import build_features
from src.models.predict import predict_risk
from src.models.train import maybe_stratified_sample


def test_build_features_excludes_transaction_id_and_target() -> None:
    """Leakage guard should always exclude TransactionID and target columns."""
    df = pd.DataFrame(
        {
            "TransactionID": [1, 2, 3],
            "TransactionDT": [1, 2, 3],
            "TransactionAmt": [10.0, 12.0, 14.0],
            "isFraud": [0, 1, 0],
        }
    )
    config = {
        "schema": {"possible_target_columns": ["isFraud", "Class"]},
        "features": {"leakage_columns": ["TransactionID"]},
        "processing": {"drop_columns": []},
    }
    features_df, _, excluded = build_features(df, config)
    assert "TransactionID" in excluded
    assert "isFraud" in excluded
    assert "TransactionID" not in features_df.columns
    assert "isFraud" in features_df.columns


def test_maybe_stratified_sample_preserves_fraud_rate() -> None:
    """Stratified sampling should preserve class ratio within tight tolerance."""
    n = 1000
    X = pd.DataFrame({"x1": range(n)})
    y = pd.Series(([1] * 50) + ([0] * 950))
    config = {"modeling": {"sample_size": 400}, "processing": {"random_state": 42}}
    X_sub, y_sub, meta = maybe_stratified_sample(X, y, config)
    assert len(X_sub) == 400
    assert meta["training_data_mode"] == "sampled"
    assert abs(float(y.mean()) - float(y_sub.mean())) < 0.002


def test_predict_fails_when_required_artifacts_are_missing(tmp_path: Path) -> None:
    """Predict should fail with actionable message when train artifacts are absent."""
    config_path = tmp_path / "config.yaml"
    config = {
        "artifacts": {
            "model_file": str(tmp_path / "artifacts/models/fraud_model.pkl"),
            "models_dir": str(tmp_path / "artifacts/models"),
        },
        "evaluation": {"threshold": {"default": 0.5}},
    }
    config_path.write_text(yaml.safe_dump(config), encoding="utf-8")

    data = pd.DataFrame([{"TransactionAmt": 10.0}])
    try:
        predict_risk(data, config_path=config_path)
    except FileNotFoundError as error:
        assert "Run `python3 -m src.models.train`" in str(error)
    else:
        raise AssertionError("predict_risk should fail when artifacts are missing")
