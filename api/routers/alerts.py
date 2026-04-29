"""
Alerts router — exposes alert history and runtime config.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

router = APIRouter()


class ThresholdUpdateRequest(BaseModel):
    """Body payload for dynamic threshold updates."""

    threshold: float = Field(..., ge=0.0, le=1.0)


@router.get("/alerts")
def get_alerts(
    request: Request,
    limit: int = Query(default=20, ge=1, le=200),
    severity: str | None = Query(default=None),
    since: str | None = Query(default=None),
) -> dict[str, Any]:
    """Return recent alerts with optional severity/since filters."""
    alerts = request.app.state.alert_engine.get_alerts(
        limit=limit,
        severity=severity,
        since=since,
    )
    return {"alerts": alerts, "total": len(alerts)}


@router.get("/alerts/stats")
def get_alerts_stats(request: Request) -> dict[str, float | int]:
    """Return alert severity counts and notification percentage."""
    return request.app.state.alert_engine.get_stats()


@router.patch("/alerts/threshold")
def update_alert_threshold(
    payload: ThresholdUpdateRequest,
    request: Request,
) -> dict[str, float]:
    """Update in-memory alert threshold without restart."""
    threshold = request.app.state.alert_engine.update_threshold(payload.threshold)
    return {"threshold": threshold}

