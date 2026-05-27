"""Schemas for Phase 5 rule-based alerts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Alert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    risk_score: float
    predicted_label: int
    severity: str
    status: str = "open"
    reason_codes: list[str] = Field(default_factory=list)
    recommended_action: str
    transaction: dict[str, Any]


class AlertEvaluateRequest(BaseModel):
    transaction: dict[str, Any]
    risk_score: float | None = None
    predicted_label: int | None = None
    severity: str | None = None


class AlertsResponse(BaseModel):
    alerts: list[Alert]

