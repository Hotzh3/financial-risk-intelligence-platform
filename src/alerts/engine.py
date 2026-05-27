"""Phase 5 alert engine orchestration."""

from __future__ import annotations

from typing import Any

from src.alerts.rules import AlertRules
from src.alerts.schemas import Alert
from src.alerts.storage import AlertStorage


class AlertEngine:
    def __init__(self, rules: AlertRules, storage: AlertStorage) -> None:
        self.rules = rules
        self.storage = storage

    def evaluate(
        self,
        *,
        transaction: dict[str, Any],
        risk_score: float,
        predicted_label: int,
        severity: str | None = None,
    ) -> Alert:
        final_severity = (severity or self.rules.severity_from_score(risk_score)).lower()
        alert = Alert(
            risk_score=float(risk_score),
            predicted_label=int(predicted_label),
            severity=final_severity,
            reason_codes=self.rules.reason_codes(
                transaction=transaction,
                risk_score=float(risk_score),
                predicted_label=int(predicted_label),
                severity=final_severity,
            ),
            recommended_action=self.rules.recommended_action(final_severity),
            transaction=transaction,
        )
        self.storage.append(alert)
        return alert

    def recent_alerts(self, limit: int = 20) -> list[Alert]:
        return self.storage.read_recent(limit=limit)

