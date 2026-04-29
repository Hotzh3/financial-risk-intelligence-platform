"""API tests for health, predictions and alert endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient

from api.main import app


def _sample_payload() -> dict[str, float | int]:
    """Build a valid prediction payload."""
    return {
        "TransactionAmt": 100.0,
        "ProductCD": 1,
        "card1": 1234,
        "card2": 111.0,
        "card3": 150.0,
        "card5": 226.0,
        "card4": 1,
        "card6": 1,
        "hour": 14,
        "V45": 1.0,
        "V86": 1.0,
        "V87": 1.0,
        "V44": 1.0,
        "V52": 1.0,
    }


def test_health_endpoint() -> None:
    """Health endpoint should return basic status info."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"


def test_predict_endpoint() -> None:
    """Predict endpoint should return risk and alert fields."""
    with TestClient(app) as client:
        response = client.post("/api/v1/predict", json=_sample_payload())
        assert response.status_code == 200
        body = response.json()
        assert "transaction_id" in body
        assert "anomaly_score" in body
        assert "alert_generated" in body


def test_alerts_and_stats_endpoints() -> None:
    """Alerts endpoints should return list and aggregate stats."""
    with TestClient(app) as client:
        client.patch("/api/v1/alerts/threshold", json={"threshold": 0.0})
        client.post("/api/v1/predict", json=_sample_payload())

        alerts_response = client.get("/api/v1/alerts")
        assert alerts_response.status_code == 200
        alerts_body = alerts_response.json()
        assert "alerts" in alerts_body
        assert "total" in alerts_body

        stats_response = client.get("/api/v1/alerts/stats")
        assert stats_response.status_code == 200
        stats_body = stats_response.json()
        assert "total_alerts" in stats_body
        assert "notified_pct" in stats_body
