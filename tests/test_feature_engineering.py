"""Tests for feature engineering helpers and pipeline output."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.engineering import (
    add_amount_features,
    add_card_features,
    add_time_features,
    run_feature_engineering,
)


def _synthetic_transactions() -> pd.DataFrame:
    """Build a tiny in-memory dataset with the columns the pipeline expects."""
    return pd.DataFrame(
        {
            "TransactionDT": [0, 3600 * 24 * 5 + 3600 * 2, 3600 * 24 * 6 + 3600 * 14],
            "TransactionAmt": [100.0, 10.75, 40.25],
            "card1": [1111, 1111, 2222],
            "card2": [100.0, 100.0, 200.0],
            "card3": [150.0, 150.0, 160.0],
            "card5": [226.0, 226.0, 224.0],
            "card4": [1, 1, 2],
            "card6": [1, 1, 2],
            "ProductCD": [1, 1, 2],
            "V45": [1.0, 2.0, 3.0],
            "V86": [0.1, 0.2, 0.3],
            "V87": [0.4, 0.5, 0.6],
            "V44": [0.7, 0.8, 0.9],
            "V52": [1.0, 1.1, 1.2],
            "V51": [0.2, 0.3, 0.4],
            "V40": [0.5, 0.6, 0.7],
            "V79": [0.8, 0.9, 1.0],
            "V39": [1.1, 1.2, 1.3],
            "V38": [1.4, 1.5, 1.6],
            "isFraud": [0, 1, 0],
        }
    )


def test_add_time_features_creates_expected_columns() -> None:
    """Time-based helpers should derive hour, weekday, and flags from seconds."""
    df = add_time_features(_synthetic_transactions()[["TransactionDT"]].copy())

    assert df["hour"].tolist() == [0, 2, 14]
    assert df["day_of_week"].tolist() == [0, 5, 6]
    assert df["is_night"].tolist() == [1, 1, 0]
    assert df["is_weekend"].tolist() == [0, 1, 1]


def test_add_amount_features_creates_expected_columns() -> None:
    """Amount helpers should derive logarithmic and cent-based features."""
    df = add_amount_features(_synthetic_transactions()[["TransactionAmt"]].copy())

    expected_logs = np.log1p([100.0, 10.75, 40.25])
    assert np.allclose(df["log_amount"], expected_logs)
    assert df["amount_cents"].tolist() == [0.0, 0.75, 0.25]
    assert df["is_round_amount"].tolist() == [1, 0, 0]


def test_add_card_features_creates_expected_aggregations() -> None:
    """Card helpers should produce per-card aggregates and deviation values."""
    df = add_card_features(_synthetic_transactions()[["TransactionAmt", "card1"]].copy())

    assert df["card1_amt_mean"].tolist() == [55.375, 55.375, 40.25]
    assert df["card1_tx_count"].tolist() == [2, 2, 1]
    assert df["card1_amt_std"].iloc[2] == 0
    assert np.isclose(df["amt_deviation"].iloc[0], (100.0 - 55.375) / (63.1094 + 1), atol=1e-3)
    assert np.isclose(df["amt_deviation"].iloc[2], 0.0)


def test_run_feature_engineering_returns_expected_shape_and_target() -> None:
    """Pipeline should return a feature matrix and target vector from tiny input."""
    X, y = run_feature_engineering(_synthetic_transactions().copy())

    assert X.shape == (3, 29)
    assert list(y) == [0, 1, 0]
    assert X.columns.tolist()[:5] == ["V45", "V86", "V87", "V44", "V52"]
    assert X.columns.tolist()[-4:] == ["card5", "card4", "card6", "ProductCD"]
