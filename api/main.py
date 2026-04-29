"""
FastAPI application for the Financial Risk Intelligence Platform.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import alerts, predictions, transactions
from src.alerts.alert_engine import AlertEngine, AlertEngineConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize shared runtime services for API routers."""
    app.state.alert_engine = AlertEngine(config=AlertEngineConfig.from_env())
    yield

app = FastAPI(
    title="Financial Risk Intelligence Platform",
    description="Fraud detection API for financial transactions",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])
app.include_router(alerts.router, prefix="/api/v1", tags=["alerts"])


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

import logging
logging.basicConfig(level=logging.DEBUG)