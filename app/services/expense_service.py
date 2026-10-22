from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group
from app.models.user import User
from app.schemas.expense import ExpenseCreate
from app.services.group_service import get_group, get_group_members, is_member
from app.services.user_service import get_user


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    # 1. Validate Group
    group = get_group(db, expense_in.group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {expense_in.group_id} not found"
        )

    # 2. Validate Payer
    payer = get_user(db, expense_in.paid_by)
    if not payer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payer user with id {expense_in.paid_by} not found"
        )

    # Payer must be in the group
    if not is_member(db, expense_in.group_id, expense_in.paid_by):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payer {payer.name} (id: {payer.id}) is not a member of group '{group.name}'"
        )

    # 3. Validate Amount
    if expense_in.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expense amount must be greater than 0"
        )

    # 4. Handle Splits
    splits_to_create = []
    split_type = "EQUAL"

    if expense_in.splits and len(expense_in.splits) > 0:
        split_type = "EXACT"
        # Validate custom splits
        splits_sum = round(sum(s.amount for s in expense_in.splits), 2)
        if abs(splits_sum - round(expense_in.amount, 2)) > 0.01:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sum of custom splits ({splits_sum}) does not equal total amount ({expense_in.amount})"
            )

        split_user_ids = set()
        for item in expense_in.splits:
            if item.user_id in split_user_ids:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate user id {item.user_id} in splits list"
                )
            split_user_ids.add(item.user_id)

            if item.amount <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Split amount for user {item.user_id} must be greater than 0"
                )

            if not is_member(db, expense_in.group_id, item.user_id):
                split_user = get_user(db, item.user_id)
                user_desc = split_user.name if split_user else f"id {item.user_id}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User {user_desc} in splits is not a member of group '{group.name}'"
                )

            splits_to_create.append((item.user_id, item.amount))
    else:
        # Default Equal Split among all members of the group
        members = get_group_members(db, expense_in.group_id)
        if not members:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create an expense for an empty group"
            )

        n = len(members)
        total_cents = int(round(expense_in.amount * 100))
        base_cents = total_cents // n
        remainder_cents = total_cents % n

        # Distribute cents so sum is exact
        for idx, member in enumerate(members):
            member_cents = base_cents + (1 if idx < remainder_cents else 0)
            member_share = round(member_cents / 100.0, 2)
            splits_to_create.append((member.id, member_share))

    # 5. Persist Expense and Splits
    db_expense = Expense(
        group_id=expense_in.group_id,
        paid_by=expense_in.paid_by,
        amount=round(expense_in.amount, 2),
        description=expense_in.description,
        category=expense_in.category or "General",
        split_type=split_type
    )
    db.add(db_expense)
    db.flush()  # Generate expense ID

    for user_id, amount in splits_to_create:
        db_split = ExpenseSplit(
            expense_id=db_expense.id,
            user_id=user_id,
            amount=amount
        )
        db.add(db_split)

    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_group_expenses(db: Session, group_id: int) -> List[Expense]:
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    return db.query(Expense).filter(Expense.group_id == group_id).order_by(Expense.created_at.desc()).all()


def search_expenses(
    db: Session,
    query: Optional[str] = None,
    group_id: Optional[int] = None,
    category: Optional[str] = None,
    paid_by: Optional[int] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
) -> List[Expense]:
    q = db.query(Expense)
    if query:
        q = q.filter(Expense.description.ilike(f"%{query}%"))
    if group_id is not None:
        q = q.filter(Expense.group_id == group_id)
    if category:
        q = q.filter(Expense.category.ilike(category))
    if paid_by is not None:
        q = q.filter(Expense.paid_by == paid_by)
    if min_amount is not None:
        q = q.filter(Expense.amount >= min_amount)
    if max_amount is not None:
        q = q.filter(Expense.amount <= max_amount)

    return q.order_by(Expense.created_at.desc()).all()
