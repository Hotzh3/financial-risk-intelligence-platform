"""Deterministic rules for severity, reason codes, and recommended actions."""

from __future__ import annotations

from typing import Any

SEVERITY_ORDER = ("low", "medium", "high", "critical")

RECOMMENDED_ACTIONS = {
    "low": "monitor",
    "medium": "review",
    "high": "manual review required",
    "critical": "block or escalate immediately",
}


class AlertRules:
    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        values = thresholds or {}
        self.low = float(values.get("low", 0.2))
        self.medium = float(values.get("medium", 0.5))
        self.high = float(values.get("high", 0.8))
        self.critical = float(values.get("critical", 0.95))

    def severity_from_score(self, risk_score: float) -> str:
        if risk_score >= self.critical:
            return "critical"
        if risk_score >= self.high:
            return "high"
        if risk_score >= self.medium:
            return "medium"
        return "low"

    def recommended_action(self, severity: str) -> str:
        return RECOMMENDED_ACTIONS.get(severity.lower(), RECOMMENDED_ACTIONS["low"])

    def reason_codes(
        self,
        *,
        transaction: dict[str, Any],
        risk_score: float,
        predicted_label: int,
        severity: str,
    ) -> list[str]:
        reasons: list[str] = []

        if risk_score >= self.high:
            reasons.append("HIGH_RISK_SCORE")
        if predicted_label == 1:
            reasons.append("MODEL_FLAGGED_FRAUD")
        if severity.lower() == "critical":
            reasons.append("CRITICAL_SEVERITY")

        amount = transaction.get("TransactionAmt")
        try:
            if amount is not None and float(amount) >= 1000.0:
                reasons.append("LARGE_TRANSACTION_AMOUNT")
        except (TypeError, ValueError):
            pass

        product = transaction.get("ProductCD")
        if product is None or str(product) not in {"W", "H", "C", "S", "R"}:
            reasons.append("UNKNOWN_PRODUCT_CODE")

        optional_fields = ["card2", "card3", "card4", "card5", "card6"]
        if not any(field in transaction for field in optional_fields):
            reasons.append("MISSING_OPTIONAL_CARD_FIELDS")

        return reasons

