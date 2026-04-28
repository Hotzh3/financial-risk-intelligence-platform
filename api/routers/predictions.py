"""
Predictions router — scores a transaction for fraud.
"""

import pickle
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from api.schemas.models import TransactionInput, PredictionOutput
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Load model once at startup
try:
    with open("models/isolation_forest.pkl", "rb") as f:
        model = pickle.load(f)
    logger.info("Model loaded successfully")
except FileNotFoundError:
    model = None
    logger.warning("Model file not found")


# Feature order must match training exactly
FEATURE_ORDER = [
    'V45', 'V86', 'V87', 'V44', 'V52', 'V51', 'V40', 'V79', 'V39', 'V38',
    'log_amount', 'amount_cents', 'is_round_amount',
    'hour', 'day_of_week', 'is_night', 'is_weekend',
    'card1_amt_mean', 'card1_amt_std', 'card1_tx_count', 'amt_deviation',
    'TransactionAmt', 'card1', 'card2', 'card3', 'card5', 'card4', 'card6', 'ProductCD'
]

def compute_features(tx: TransactionInput) -> pd.DataFrame:
    data = {
        "TransactionAmt": tx.TransactionAmt,
        "ProductCD": tx.ProductCD,
        "card1": tx.card1,
        "card2": tx.card2,
        "card3": tx.card3,
        "card5": tx.card5,
        "card4": tx.card4,
        "card6": tx.card6,
        "hour": tx.hour,
        "V45": tx.V45,
        "V86": tx.V86,
        "V87": tx.V87,
        "V44": tx.V44,
        "V52": tx.V52,
        "log_amount": np.log1p(tx.TransactionAmt),
        "amount_cents": round(tx.TransactionAmt % 1, 2),
        "is_round_amount": int(tx.TransactionAmt % 1 == 0),
        "is_night": int(0 <= tx.hour <= 6),
        "day_of_week": 0,
        "is_weekend": 0,
        "card1_amt_mean": tx.TransactionAmt,
        "card1_amt_std": 0,
        "card1_tx_count": 1,
        "amt_deviation": 0,
        "V51": 1.0, "V40": 1.0, "V79": 1.0,
        "V39": 1.0, "V38": 1.0,
    }
    return pd.DataFrame([data])[FEATURE_ORDER]


@router.post("/predict", response_model=PredictionOutput)
def predict(transaction: TransactionInput):
    """Score a single transaction for fraud risk."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    features = compute_features(transaction)
    score = -model.decision_function(features)[0]
    score_normalized = float(np.clip((score + 0.5) / 1.0, 0, 1))

    if score_normalized >= 0.7:
        risk_level = "HIGH"
        is_fraud = True
    elif score_normalized >= 0.4:
        risk_level = "MEDIUM"
        is_fraud = False
    else:
        risk_level = "LOW"
        is_fraud = False

    import uuid
    return PredictionOutput(
        transaction_id=str(uuid.uuid4()),
        anomaly_score=round(score_normalized, 4),
        risk_level=risk_level,
        is_fraud=is_fraud,
        message=f"Transaction classified as {risk_level} risk"
    )