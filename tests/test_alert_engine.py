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


def test_alert_engine_does_not_generate_alert_below_threshold(tmp_path: Path) -> None:
    """Scores below the configured threshold should not persist alerts."""
    engine = AlertEngine(
        config=AlertEngineConfig(
            threshold=0.7,
            db_path=str(tmp_path / "alerts_below_threshold.db"),
        )
    )

    result = engine.evaluate(
        transaction_id="tx-low",
        anomaly_score=0.69,
        payload={"TransactionAmt": 42.5},
    )

    assert result is None
    assert engine.get_alerts(limit=10) == []
    assert engine.get_stats()["total_alerts"] == 0


def test_alert_engine_update_threshold_changes_runtime_behavior(tmp_path: Path) -> None:
    """Updating the threshold should affect later evaluations."""
    engine = AlertEngine(
        config=AlertEngineConfig(
            threshold=0.8,
            db_path=str(tmp_path / "alerts_threshold_update.db"),
        )
    )

    assert engine.evaluate("tx-before", 0.7, {"TransactionAmt": 100.0}) is None
    assert engine.update_threshold(0.6) == 0.6

    result = engine.evaluate("tx-after", 0.7, {"TransactionAmt": 100.0})

    assert result is not None
    assert result["severity"] == "MEDIUM"
    assert len(engine.get_alerts(limit=10)) == 1


def test_alert_engine_filters_alerts_by_severity_and_reports_stats(tmp_path: Path) -> None:
    """Alert queries and aggregate stats should reflect severity accurately."""
    engine = AlertEngine(
        config=AlertEngineConfig(
            threshold=0.5,
            db_path=str(tmp_path / "alerts_stats.db"),
        )
    )

    engine.evaluate("tx-medium", 0.6, {"TransactionAmt": 125.0})
    engine.evaluate("tx-high", 0.91, {"TransactionAmt": 950.0})

    medium_alerts = engine.get_alerts(limit=10, severity="medium")
    high_alerts = engine.get_alerts(limit=10, severity="HIGH")
    stats = engine.get_stats()

    assert len(medium_alerts) == 1
    assert medium_alerts[0]["transaction_id"] == "tx-medium"
    assert medium_alerts[0]["severity"] == "MEDIUM"

    assert len(high_alerts) == 1
    assert high_alerts[0]["transaction_id"] == "tx-high"
    assert high_alerts[0]["severity"] == "HIGH"

    assert stats == {
        "total_alerts": 2,
        "low": 0,
        "medium": 1,
        "high": 1,
        "notified_pct": 0.0,
    }
