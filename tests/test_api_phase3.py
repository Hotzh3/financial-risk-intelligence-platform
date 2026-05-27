"""Tests for Phase 3 FastAPI prediction service."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.dependencies import get_prediction_service
from src.api.main import app


def test_health_returns_ok() -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "financial-risk-intelligence-api",
    }


def test_model_metadata_returns_payload() -> None:
    with TestClient(app) as client:
        response = client.get("/model/metadata")
    assert response.status_code == 200
    body = response.json()
    assert "artifacts" in body
    assert "threshold" in body


def test_predict_validates_payload_shape() -> None:
    with TestClient(app) as client:
        response = client.post("/predict", json={})
    assert response.status_code == 422


def test_predict_returns_scoring_fields() -> None:
    payload = {
        "transaction": {
            "TransactionAmt": 100.0,
            "ProductCD": "W",
            "card1": 1234,
        }
    }
    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        body = response.json()
        assert "risk_score" in body
        assert "predicted_label" in body
        assert "severity" in body


def test_predict_returns_controlled_error_when_artifacts_missing() -> None:
    class MissingArtifactService:
        def predict_one(self, transaction: dict) -> dict:  # pragma: no cover - simple stub
            raise FileNotFoundError("Missing required artifacts")

    app.dependency_overrides[get_prediction_service] = lambda: MissingArtifactService()
    try:
        with TestClient(app) as client:
            response = client.post("/predict", json={"transaction": {"TransactionAmt": 10}})
        assert response.status_code == 503
        assert "Missing required artifacts" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
