"""Focused Phase 5 regression tests."""

from __future__ import annotations

from src.alerts.rules import AlertRules


def test_severity_thresholds() -> None:
    rules = AlertRules({"low": 0.2, "medium": 0.5, "high": 0.8, "critical": 0.95})
    assert rules.severity_from_score(0.1) == "low"
    assert rules.severity_from_score(0.5) == "medium"
    assert rules.severity_from_score(0.8) == "high"
    assert rules.severity_from_score(0.95) == "critical"


def test_recommended_actions() -> None:
    rules = AlertRules()
    assert rules.recommended_action("low") == "monitor"
    assert rules.recommended_action("medium") == "review"
    assert rules.recommended_action("high") == "manual review required"
    assert rules.recommended_action("critical") == "block or escalate immediately"

