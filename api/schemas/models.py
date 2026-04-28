"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    TransactionAmt: float = Field(..., example=100.0)
    ProductCD: int = Field(..., example=1)
    card1: int = Field(..., example=1234)
    card2: float = Field(..., example=111.0)
    card3: float = Field(..., example=150.0)
    card5: float = Field(..., example=226.0)
    card4: int = Field(..., example=1)
    card6: int = Field(..., example=1)
    hour: int = Field(..., example=14)
    V45: float = Field(..., example=1.0)
    V86: float = Field(..., example=1.0)
    V87: float = Field(..., example=1.0)
    V44: float = Field(..., example=1.0)
    V52: float = Field(..., example=1.0)


class PredictionOutput(BaseModel):
    transaction_id: str
    anomaly_score: float
    risk_level: str
    is_fraud: bool
    message: str