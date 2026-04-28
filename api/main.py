"""
FastAPI application for the Financial Risk Intelligence Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import predictions, transactions

app = FastAPI(
    title="Financial Risk Intelligence Platform",
    description="Fraud detection API for financial transactions",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predictions.router, prefix="/api/v1", tags=["predictions"])
app.include_router(transactions.router, prefix="/api/v1", tags=["transactions"])


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1.0"}

import logging
logging.basicConfig(level=logging.DEBUG)