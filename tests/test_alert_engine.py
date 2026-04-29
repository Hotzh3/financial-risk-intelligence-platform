"""Unit tests for AlertEngine behavior."""

from __future__ import annotations

from pathlib import Path

from src.alerts.alert_engine import AlertEngine, AlertEngineConfig


def test_alert_engine_evaluate_generates_alert(tmp_path: Path) -> None:
    """Engine should generate and store an alert when score exceeds threshold."""
    config = AlertEngineConfig(
        threshold=0.5,
        db_path=str(tmp_path / "alerts_test.db"),
    )
    engine = AlertEngine(config=config)
    result = engine.evaluate(
        transaction_id="tx-1",
        anomaly_score=0.8,
        payload={"TransactionAmt": 1500.0, "risk_level": "HIGH"},
    )

    assert result is not None
    assert result["severity"] in {"MEDIUM", "HIGH"}
    assert result["transaction_id"] == "tx-1"

    alerts = engine.get_alerts(limit=10)
    assert len(alerts) == 1
