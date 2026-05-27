"""Lightweight JSONL storage for alerts."""

from __future__ import annotations

import json
from pathlib import Path

from src.alerts.schemas import Alert


class AlertStorage:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def append(self, alert: Alert) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(alert.model_dump(), ensure_ascii=True) + "\n")

    def read_recent(self, limit: int = 20) -> list[Alert]:
        if not self.path.exists():
            return []

        lines = self.path.read_text(encoding="utf-8").splitlines()
        alerts: list[Alert] = []
        for line in lines[-max(limit, 0) :]:
            line = line.strip()
            if not line:
                continue
            alerts.append(Alert(**json.loads(line)))
        return list(reversed(alerts))

