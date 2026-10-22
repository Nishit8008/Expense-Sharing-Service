from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.settlement import SettlementCreate, SettlementResponse
from app.services import settlement_service

router = APIRouter(prefix="/settlements", tags=["Settlements"])


def _format_settlement(st) -> SettlementResponse:
    return SettlementResponse(
        id=st.id,
        payer_id=st.payer_id,
        payer_name=st.payer.name,
        payee_id=st.payee_id,
        payee_name=st.payee.name,
        amount=st.amount,
        group_id=st.group_id,
        notes=st.notes,
        created_at=st.created_at
    )


@router.post("", response_model=SettlementResponse, status_code=status.HTTP_201_CREATED)
def record_settlement(settlement_in: SettlementCreate, db: Session = Depends(get_db)):
    """
    Record a settlement payment between two users.
    Offsets outstanding balances between the payer and payee.
    """
    settlement = settlement_service.create_settlement(db, settlement_in)
    return _format_settlement(settlement)


@router.get("", response_model=List[SettlementResponse])
def list_settlements(
    group_id: Optional[int] = Query(None, description="Filter settlements by group ID"),
    db: Session = Depends(get_db)
):
    """List recorded settlements."""
    settlements = settlement_service.get_settlements(db, group_id=group_id)
    return [_format_settlement(st) for st in settlements]
