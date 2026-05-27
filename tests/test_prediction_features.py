"""Tests for inference-side feature alignment before model prediction."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.models.predict import _prepare_input


def test_prepare_input_matches_expected_shape_and_column_order() -> None:
    """Inference input should align to training feature order with NaN fill for missing columns."""
    feature_columns = ["TransactionAmt", "ProductCD", "card1", "V45", "V86", "V87"]
    payload = pd.DataFrame(
        [
            {
                "TransactionAmt": 100.25,
                "ProductCD": "W",
                "card1": 1234,
                "V45": 1.0,
            }
        ]
    )

    aligned = _prepare_input(payload, feature_columns)

    assert aligned.shape == (1, len(feature_columns))
    assert aligned.columns.tolist() == feature_columns
    assert aligned.loc[0, "TransactionAmt"] == 100.25
    assert aligned.loc[0, "ProductCD"] == "W"
    assert np.isnan(aligned.loc[0, "V86"])
    assert np.isnan(aligned.loc[0, "V87"])
