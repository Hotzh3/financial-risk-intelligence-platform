"""
Transactions router — returns transaction history.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/transactions")
def get_transactions():
    """Placeholder — returns mock transactions."""
    return {
        "transactions": [],
        "total": 0,
        "message": "Database integration coming in next phase"
    }


@router.get("/metrics")
def get_metrics():
    """Returns system KPIs."""
    return {
        "total_transactions": 590540,
        "fraud_rate": 0.035,
        "model": "Isolation Forest",
        "roc_auc": 0.7120,
        "status": "operational"
    }