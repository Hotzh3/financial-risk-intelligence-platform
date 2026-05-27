"""API routes for health, metadata, prediction, and alerts."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.dependencies import get_prediction_service
from src.api.schemas import (
    AlertEvaluateRequest,
    AlertResponse,
    AlertsListResponse,
    BatchPredictRequest,
    BatchPredictResponse,
    HealthResponse,
    ModelMetadataResponse,
    PredictRequest,
    PredictResult,
)
from src.api.services import PredictionService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="financial-risk-intelligence-api")


@router.get("/model/metadata", response_model=ModelMetadataResponse)
def model_metadata(
    service: PredictionService = Depends(get_prediction_service),
) -> ModelMetadataResponse:
    payload = service.get_model_metadata()
    return ModelMetadataResponse(**payload)


@router.post("/predict", response_model=PredictResult)
def predict(
    request: PredictRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> PredictResult:
    try:
        payload = service.predict_one(request.transaction)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return PredictResult(**payload)


@router.post("/predict/batch", response_model=BatchPredictResponse)
def predict_batch(
    request: BatchPredictRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> BatchPredictResponse:
    try:
        predictions = service.predict_batch(request.transactions)
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return BatchPredictResponse(predictions=[PredictResult(**item) for item in predictions])


@router.get("/alerts", response_model=AlertsListResponse)
def get_alerts(
    limit: int = Query(default=20, ge=1, le=200),
    service: PredictionService = Depends(get_prediction_service),
) -> AlertsListResponse:
    return AlertsListResponse(alerts=[AlertResponse(**item) for item in service.get_alerts(limit=limit)])


@router.post("/alerts/evaluate", response_model=AlertResponse)
def evaluate_alert(
    request: AlertEvaluateRequest,
    service: PredictionService = Depends(get_prediction_service),
) -> AlertResponse:
    try:
        payload = service.evaluate_alert(
            transaction=request.transaction,
            risk_score=request.risk_score,
            predicted_label=request.predicted_label,
            severity=request.severity,
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return AlertResponse(**payload)

