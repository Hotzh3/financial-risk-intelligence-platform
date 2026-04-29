"""
Alert engine for fraud scoring notifications and persistence.
"""

from __future__ import annotations

import os
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AlertEngineConfig:
    """Runtime configuration for alert engine behavior."""

    threshold: float = 0.7
    email_enabled: bool = False
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = ""
    email_to: str = ""
    db_path: str = "alerts.db"

    @classmethod
    def from_env(cls) -> "AlertEngineConfig":
        """Build config from process environment variables."""
        threshold = float(os.getenv("ALERT_THRESHOLD", "0.7"))
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        email_enabled = os.getenv("ALERT_EMAIL_ENABLED", "false").lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        return cls(
            threshold=threshold,
            email_enabled=email_enabled,
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=smtp_port,
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            email_from=os.getenv("ALERT_EMAIL_FROM", ""),
            email_to=os.getenv("ALERT_EMAIL_TO", ""),
            db_path=os.getenv("ALERT_DB_PATH", "alerts.db"),
        )


class AlertEngine:
    """Evaluates prediction events and stores generated alerts."""

    def __init__(self, config: AlertEngineConfig) -> None:
        self.config = config
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        """Create a SQLite connection using row dictionaries."""
        conn = sqlite3.connect(self.config.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create alerts table if it does not exist."""
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id TEXT PRIMARY KEY,
                    transaction_id TEXT NOT NULL,
                    anomaly_score REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    amount REAL NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    notified INTEGER NOT NULL
                )
                """
            )
            conn.commit()
        logger.info("AlertEngine initialized with db=%s", self.config.db_path)

    def _severity_from_score(self, score: float) -> str:
        """Map anomaly score to severity bands."""
        if score >= 0.85:
            return "HIGH"
        if score >= self.config.threshold:
            return "MEDIUM"
        return "LOW"

    def evaluate(
        self,
        transaction_id: str,
        anomaly_score: float,
        payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Evaluate a prediction event and persist alert when threshold is exceeded."""
        if anomaly_score < self.config.threshold:
            return None

        amount = float(payload.get("TransactionAmt", 0.0))
        alert = {
            "alert_id": str(uuid.uuid4()),
            "transaction_id": transaction_id,
            "anomaly_score": round(float(anomaly_score), 4),
            "risk_level": payload.get("risk_level", self._severity_from_score(anomaly_score)),
            "amount": amount,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "severity": self._severity_from_score(anomaly_score),
            "notified": bool(self.config.email_enabled and self._send_notification(amount)),
        }
        self._store_alert(alert)
        return alert

    def _store_alert(self, alert: dict[str, Any]) -> None:
        """Insert a generated alert into SQLite."""
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO alerts (
                    alert_id,
                    transaction_id,
                    anomaly_score,
                    risk_level,
                    amount,
                    timestamp,
                    status,
                    severity,
                    notified
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    alert["alert_id"],
                    alert["transaction_id"],
                    alert["anomaly_score"],
                    alert["risk_level"],
                    alert["amount"],
                    alert["timestamp"],
                    alert["status"],
                    alert["severity"],
                    int(alert["notified"]),
                ),
            )
            conn.commit()

    def _send_notification(self, amount: float) -> bool:
        """Placeholder notification hook (email/webhook can be added later)."""
        logger.info(
            "Notification requested=%s smtp_host=%s amount=%.2f",
            self.config.email_enabled,
            self.config.smtp_host or "unset",
            amount,
        )
        return self.config.email_enabled and bool(self.config.email_to)

    def get_alerts(
        self,
        limit: int = 20,
        severity: str | None = None,
        since: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return latest alerts with optional filters."""
        query = "SELECT * FROM alerts"
        filters: list[str] = []
        params: list[Any] = []
        if severity:
            filters.append("severity = ?")
            params.append(severity.upper())
        if since:
            filters.append("timestamp >= ?")
            params.append(since)
        if filters:
            query += " WHERE " + " AND ".join(filters)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get_stats(self) -> dict[str, float | int]:
        """Return aggregate alert metrics for dashboard/API."""
        with self._connect() as conn:
            total = int(conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0])
            low = int(conn.execute("SELECT COUNT(*) FROM alerts WHERE severity='LOW'").fetchone()[0])
            medium = int(
                conn.execute("SELECT COUNT(*) FROM alerts WHERE severity='MEDIUM'").fetchone()[0]
            )
            high = int(conn.execute("SELECT COUNT(*) FROM alerts WHERE severity='HIGH'").fetchone()[0])
            notified = int(conn.execute("SELECT COUNT(*) FROM alerts WHERE notified=1").fetchone()[0])
        notified_pct = (notified / total) * 100 if total else 0.0
        return {
            "total_alerts": total,
            "low": low,
            "medium": medium,
            "high": high,
            "notified_pct": round(notified_pct, 2),
        }

    def update_threshold(self, threshold: float) -> float:
        """Update threshold at runtime and return the new value."""
        self.config.threshold = float(threshold)
        logger.info("Alert threshold updated to %.4f", self.config.threshold)
        return self.config.threshold
