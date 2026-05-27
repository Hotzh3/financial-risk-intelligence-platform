"""HTTP client helpers for the Streamlit dashboard."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{get_api_base_url()}{path}"
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.request(method=method, url=url, json=payload)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
            return {"data": data}
    except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as exc:
        return {"error": str(exc)}


def get_health() -> dict[str, Any]:
    return _request("GET", "/health")


def get_model_metadata() -> dict[str, Any]:
    return _request("GET", "/model/metadata")


def predict_one(transaction: dict[str, Any]) -> dict[str, Any]:
    return _request("POST", "/predict", payload={"transaction": transaction})


def predict_batch(transactions: list[dict[str, Any]]) -> dict[str, Any]:
    return _request("POST", "/predict/batch", payload={"transactions": transactions})


def get_alerts(limit: int = 20) -> dict[str, Any]:
    return _request("GET", f"/alerts?limit={limit}")


def evaluate_alert(
    transaction: dict[str, Any],
    risk_score: float | None = None,
    predicted_label: int | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"transaction": transaction}
    if risk_score is not None:
        payload["risk_score"] = risk_score
    if predicted_label is not None:
        payload["predicted_label"] = predicted_label
    if severity is not None:
        payload["severity"] = severity
    return _request("POST", "/alerts/evaluate", payload=payload)

