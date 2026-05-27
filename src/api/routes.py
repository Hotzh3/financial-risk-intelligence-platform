"""API routes for health, metadata, and risk prediction."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_prediction_service
from src.api.schemas import (
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

