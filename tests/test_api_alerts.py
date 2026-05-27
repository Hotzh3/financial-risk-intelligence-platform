"""API tests for Phase 5 alert endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.dependencies import get_prediction_service
from src.api.main import app


class _StubService:
    def __init__(self) -> None:
        self._alerts: list[dict] = []

    def get_alerts(self, limit: int = 20) -> list[dict]:
        return self._alerts[:limit]

    def evaluate_alert(
        self,
        transaction: dict,
        risk_score: float | None = None,
        predicted_label: int | None = None,
        severity: str | None = None,
    ) -> dict:
        alert = {
            "alert_id": "a-1",
            "timestamp": "2026-01-01T00:00:00+00:00",
            "risk_score": risk_score if risk_score is not None else 0.7,
            "predicted_label": predicted_label if predicted_label is not None else 1,
            "severity": severity or "high",
            "status": "open",
            "reason_codes": ["MODEL_FLAGGED_FRAUD"],
            "recommended_action": "manual review required",
            "transaction": transaction,
        }
        self._alerts = [alert] + self._alerts
        return alert


def test_alerts_returns_controlled_response() -> None:
    service = _StubService()
    app.dependency_overrides[get_prediction_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.get("/alerts")
        assert response.status_code == 200
        assert response.json() == {"alerts": []}
    finally:
        app.dependency_overrides.clear()


def test_alerts_evaluate_returns_alert_object() -> None:
    service = _StubService()
    app.dependency_overrides[get_prediction_service] = lambda: service
    try:
        with TestClient(app) as client:
            response = client.post(
                "/alerts/evaluate",
                json={"transaction": {"TransactionAmt": 120.5, "ProductCD": "W", "card1": 1000}},
            )
        assert response.status_code == 200
        body = response.json()
        assert body["alert_id"] == "a-1"
        assert body["severity"] == "high"
        assert body["recommended_action"] == "manual review required"
    finally:
        app.dependency_overrides.clear()

