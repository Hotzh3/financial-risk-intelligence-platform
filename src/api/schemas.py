"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class ArtifactStatus(BaseModel):
    path: str
    exists: bool


class ModelMetadataResponse(BaseModel):
    model_name: str | None
    target_column: str | None
    number_of_features: int | None
    threshold: float | None
    artifacts: dict[str, ArtifactStatus]


class PredictRequest(BaseModel):
    transaction: dict[str, Any]


class PredictResult(BaseModel):
    risk_score: float
    predicted_label: int
    severity: str


class BatchPredictRequest(BaseModel):
    transactions: list[dict[str, Any]]


class BatchPredictResponse(BaseModel):
    predictions: list[PredictResult]
