from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.analytics import SimplifiedSettlementResponse
from app.services import balance_service, analytics_service

router = APIRouter(prefix="/balances", tags=["Balances"])


@router.get("")
def get_balances(
    group_id: Optional[int] = Query(None, description="Optional group ID to filter balances"),
    db: Session = Depends(get_db)
):
    """
    Calculate and return balances between users.
    Output follows the exact structured format:
    {
      "Rahul": {
        "owes": {
          "Mohit": 400
        }
      },
      "Ankit": {
        "owes": {
          "Mohit": 400
        }
      }
    }
    """
    return balance_service.calculate_balances(db, group_id=group_id)


@router.get("/simplify", response_model=SimplifiedSettlementResponse)
def get_simplified_balances(
    group_id: Optional[int] = Query(None, description="Optional group ID to scope simplification"),
    db: Session = Depends(get_db)
):
    """
    Product Enhancement: Smart Debt Simplification Algorithm.
    Applies a Min-Cash-Flow graph simplification algorithm to minimize
    the total number of transactions needed for the group to be fully settled.
    """
    return analytics_service.get_simplified_settlements(db, group_id=group_id)
