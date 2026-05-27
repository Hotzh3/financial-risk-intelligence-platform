"""Lightweight tests for Phase 4 dashboard helpers."""

from __future__ import annotations

import json
from pathlib import Path

import httpx

from dashboard.components.metrics import extract_core_metrics, load_json_report
from dashboard.utils import api_client


class _DummyResponse:
    def __init__(self, payload: dict, raise_error: Exception | None = None) -> None:
        self._payload = payload
        self._raise_error = raise_error

    def raise_for_status(self) -> None:
        if self._raise_error is not None:
            raise self._raise_error

    def json(self) -> dict:
        return self._payload


class _DummyClient:
    def __init__(self, response: _DummyResponse | None = None, request_error: Exception | None = None) -> None:
        self._response = response
        self._request_error = request_error

    def __enter__(self) -> "_DummyClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def request(self, method: str, url: str, json: dict | None = None):  # noqa: ARG002
        if self._request_error is not None:
            raise self._request_error
        return self._response


def test_get_health_success(monkeypatch) -> None:
    response = _DummyResponse({"status": "ok", "service": "api"})
    monkeypatch.setattr(api_client.httpx, "Client", lambda timeout=5.0: _DummyClient(response=response))
    payload = api_client.get_health()
    assert payload["status"] == "ok"


def test_get_health_connection_error(monkeypatch) -> None:
    request = httpx.Request("GET", "http://127.0.0.1:8000/health")
    error = httpx.ConnectError("down", request=request)
    monkeypatch.setattr(api_client.httpx, "Client", lambda timeout=5.0: _DummyClient(request_error=error))
    payload = api_client.get_health()
    assert "error" in payload


def test_load_json_report_returns_none_for_missing_file(tmp_path: Path) -> None:
    report = load_json_report(tmp_path / "missing.json")
    assert report is None


def test_extract_core_metrics_returns_expected_fields() -> None:
    payload = {
        "precision": 0.1,
        "recall": 0.2,
        "f1": 0.3,
        "roc_auc": 0.4,
        "pr_auc": 0.5,
        "threshold": 0.6,
    }
    metrics = extract_core_metrics(payload)
    assert metrics == payload


def test_load_json_report_with_valid_dict(tmp_path: Path) -> None:
    file_path = tmp_path / "model_metrics.json"
    file_path.write_text(json.dumps({"precision": 0.9}), encoding="utf-8")
    report = load_json_report(file_path)
    assert report == {"precision": 0.9}
