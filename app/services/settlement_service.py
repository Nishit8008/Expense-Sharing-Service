from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.settlement import Settlement
from app.models.user import User
from app.models.group import Group
from app.schemas.settlement import SettlementCreate
from app.services.group_service import get_group, is_member
from app.services.user_service import get_user


def create_settlement(db: Session, settlement_in: SettlementCreate) -> Settlement:
    if settlement_in.payer_id == settlement_in.payee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payer and payee cannot be the same user"
        )

    payer = get_user(db, settlement_in.payer_id)
    if not payer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer user with id {settlement_in.payer_id} not found"
        )

    payee = get_user(db, settlement_in.payee_id)
    if not payee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payee user with id {settlement_in.payee_id} not found"
        )

    if settlement_in.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Settlement amount must be greater than 0"
        )

    if settlement_in.group_id is not None:
        group = get_group(db, settlement_in.group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {settlement_in.group_id} not found"
            )
        if not is_member(db, settlement_in.group_id, settlement_in.payer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payer {payer.name} is not a member of group '{group.name}'"
            )
        if not is_member(db, settlement_in.group_id, settlement_in.payee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payee {payee.name} is not a member of group '{group.name}'"
            )

    db_settlement = Settlement(
        group_id=settlement_in.group_id,
        payer_id=settlement_in.payer_id,
        payee_id=settlement_in.payee_id,
        amount=round(settlement_in.amount, 2),
        notes=settlement_in.notes
    )
    db.add(db_settlement)
    db.commit()
    db.refresh(db_settlement)
    return db_settlement


def get_settlements(db: Session, group_id: Optional[int] = None) -> List[Settlement]:
    q = db.query(Settlement)
    if group_id is not None:
        q = q.filter(Settlement.group_id == group_id)
    return q.order_by(Settlement.created_at.desc()).all()
