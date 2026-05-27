"""Unit tests for Phase 5 alert engine behavior."""

from __future__ import annotations

from pathlib import Path

from src.alerts.engine import AlertEngine
from src.alerts.rules import AlertRules
from src.alerts.storage import AlertStorage


def _engine(path: Path) -> AlertEngine:
    return AlertEngine(
        rules=AlertRules(thresholds={"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 0.95}),
        storage=AlertStorage(path),
    )


def test_severity_and_action_mapping(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "alerts.jsonl")
    alert = engine.evaluate(
        transaction={"TransactionAmt": 50.0, "ProductCD": "W", "card1": 1},
        risk_score=0.97,
        predicted_label=1,
    )
    assert alert.severity == "critical"
    assert alert.recommended_action == "block or escalate immediately"


def test_reason_codes_generation(tmp_path: Path) -> None:
    engine = _engine(tmp_path / "alerts.jsonl")
    alert = engine.evaluate(
        transaction={"TransactionAmt": 1800.0, "ProductCD": "X", "card1": 1234},
        risk_score=0.9,
        predicted_label=1,
    )
    assert "HIGH_RISK_SCORE" in alert.reason_codes
    assert "MODEL_FLAGGED_FRAUD" in alert.reason_codes
    assert "LARGE_TRANSACTION_AMOUNT" in alert.reason_codes
    assert "UNKNOWN_PRODUCT_CODE" in alert.reason_codes
    assert "MISSING_OPTIONAL_CARD_FIELDS" in alert.reason_codes


def test_jsonl_storage_append_and_read_recent(tmp_path: Path) -> None:
    path = tmp_path / "alerts.jsonl"
    engine = _engine(path)

    engine.evaluate(
        transaction={"TransactionAmt": 50.0, "ProductCD": "W", "card1": 1},
        risk_score=0.3,
        predicted_label=0,
    )
    engine.evaluate(
        transaction={"TransactionAmt": 500.0, "ProductCD": "H", "card1": 2},
        risk_score=0.6,
        predicted_label=1,
    )

    recent = engine.recent_alerts(limit=2)
    assert len(recent) == 2
    assert recent[0].risk_score == 0.6
    assert recent[1].risk_score == 0.3

