from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseResponse, SplitResponse
from app.services import expense_service

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _format_expense(expense) -> ExpenseResponse:
    splits_data = [
        SplitResponse(user_id=s.user_id, user_name=s.user.name, amount=s.amount)
        for s in expense.splits
    ]
    return ExpenseResponse(
        id=expense.id,
        description=expense.description,
        amount=expense.amount,
        paid_by=expense.payer.name,
        paid_by_id=expense.paid_by,
        category=expense.category,
        split_type=expense.split_type,
        created_at=expense.created_at,
        splits=splits_data
    )


@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def add_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    """
    Record a shared expense.
    - Amount must be greater than 0.
    - Expense must belong to a valid group.
    - Defaults to equal split among all members of the group.
    - Supports custom unequal splits via the optional `splits` field.
    """
    expense = expense_service.create_expense(db, expense_in)
    return _format_expense(expense)


@router.get("/search", response_model=List[ExpenseResponse])
def search_expenses(
    q: Optional[str] = Query(None, description="Search query matching expense description"),
    group_id: Optional[int] = Query(None, description="Filter by group ID"),
    category: Optional[str] = Query(None, description="Filter by category (Food, Travel, etc.)"),
    paid_by: Optional[int] = Query(None, description="Filter by payer user ID"),
    min_amount: Optional[float] = Query(None, description="Minimum expense amount"),
    max_amount: Optional[float] = Query(None, description="Maximum expense amount"),
    db: Session = Depends(get_db)
):
    """
    Product Enhancement: Advanced search & filtering for expenses across groups,
    categories, amounts, and keywords.
    """
    expenses = expense_service.search_expenses(
        db,
        query=q,
        group_id=group_id,
        category=category,
        paid_by=paid_by,
        min_amount=min_amount,
        max_amount=max_amount
    )
    return [_format_expense(e) for e in expenses]
