"""Tests for API-side feature assembly before model inference."""

from __future__ import annotations

import numpy as np

from api.routers.predictions import FEATURE_ORDER, compute_features
from api.schemas.models import TransactionInput


def test_compute_features_matches_expected_shape_and_column_order() -> None:
    """Runtime feature assembly should preserve the trained feature order."""
    tx = TransactionInput(
        TransactionAmt=100.25,
        ProductCD=1,
        card1=1234,
        card2=111.0,
        card3=150.0,
        card5=226.0,
        card4=1,
        card6=1,
        hour=3,
        V45=1.0,
        V86=2.0,
        V87=3.0,
        V44=4.0,
        V52=5.0,
    )

    features = compute_features(tx)

    assert features.shape == (1, len(FEATURE_ORDER))
    assert features.columns.tolist() == FEATURE_ORDER
    assert features.loc[0, "TransactionAmt"] == 100.25
    assert np.isclose(features.loc[0, "log_amount"], np.log1p(100.25))
    assert features.loc[0, "amount_cents"] == 0.25
    assert features.loc[0, "is_round_amount"] == 0
    assert features.loc[0, "is_night"] == 1
