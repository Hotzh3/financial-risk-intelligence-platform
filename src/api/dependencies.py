"""Dependency providers for API routes."""

from __future__ import annotations

from src.api.services import PredictionService


def get_prediction_service() -> PredictionService:
    return PredictionService()

