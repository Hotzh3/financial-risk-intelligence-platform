"""FastAPI entrypoint for Financial Risk Intelligence API (Phase 3)."""

from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import router

app = FastAPI(
    title="Financial Risk Intelligence API",
    version="0.1.0",
    description="REST API for fraud risk scoring using trained model artifacts.",
)

app.include_router(router)

