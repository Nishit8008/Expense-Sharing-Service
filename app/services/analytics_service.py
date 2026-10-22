from collections import defaultdict
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.expense import Expense, ExpenseSplit
from app.models.group import Group
from app.models.user import User
from app.schemas.analytics import (
    GroupAnalyticsResponse,
    CategorySpend,
    UserSpend,
    SimplifiedSettlementResponse,
    SimplifiedTransaction,
)
from app.services.group_service import get_group, get_group_members
from app.services.balance_service import calculate_net_user_balances
from app.utils.debt_simplifier import simplify_debts


def get_group_analytics(db: Session, group_id: int) -> GroupAnalyticsResponse:
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )

    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()
    members = get_group_members(db, group_id)
    user_names = {u.id: u.name for u in db.query(User).all()}

    total_group_spending = round(sum(e.amount for e in expenses), 2)
    total_expenses_count = len(expenses)

    # Category breakdown
    cat_amounts: Dict[str, float] = defaultdict(float)
    cat_counts: Dict[str, int] = defaultdict(int)

    for exp in expenses:
        cat = exp.category.strip().title() if exp.category else "General"
        cat_amounts[cat] += exp.amount
        cat_counts[cat] += 1

    category_breakdown: List[CategorySpend] = []
    for cat, amt in sorted(cat_amounts.items(), key=lambda x: x[1], reverse=True):
        pct = round((amt / total_group_spending * 100), 1) if total_group_spending > 0 else 0.0
        category_breakdown.append(CategorySpend(
            category=cat,
            amount=round(amt, 2),
            percentage=pct,
            expense_count=cat_counts[cat]
        ))

    # Member spending (total paid, total share)
    user_paid: Dict[int, float] = defaultdict(float)
    user_share: Dict[int, float] = defaultdict(float)

    for exp in expenses:
        user_paid[exp.paid_by] += exp.amount
        splits = db.query(ExpenseSplit).filter(ExpenseSplit.expense_id == exp.id).all()
        for s in splits:
            user_share[s.user_id] += s.amount

    member_spending: List[UserSpend] = []
    top_spender_name = None
    max_paid = -1.0

    for m in members:
        paid = round(user_paid[m.id], 2)
        share = round(user_share[m.id], 2)
        net = round(paid - share, 2)
        if paid > max_paid and paid > 0:
            max_paid = paid
            top_spender_name = m.name

        member_spending.append(UserSpend(
            user_id=m.id,
            user_name=m.name,
            total_paid=paid,
            total_share=share,
            net_balance=net
        ))

    return GroupAnalyticsResponse(
        group_id=group.id,
        group_name=group.name,
        total_group_spending=total_group_spending,
        total_expenses_count=total_expenses_count,
        category_breakdown=category_breakdown,
        member_spending=member_spending,
        top_spender=top_spender_name
    )


def get_simplified_settlements(db: Session, group_id: Optional[int] = None) -> SimplifiedSettlementResponse:
    if group_id is not None:
        group = get_group(db, group_id)
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )

    user_names = {u.id: u.name for u in db.query(User).all()}
    net_balances = calculate_net_user_balances(db, group_id=group_id)

    raw_txns = simplify_debts(net_balances, user_names)

    txns = [SimplifiedTransaction(**t) for t in raw_txns]

    # Calculate how many transactions were eliminated compared to pairwise debts
    # In full mesh, N users could have up to N*(N-1)/2 transactions
    active_users = [uid for uid, bal in net_balances.items() if abs(bal) > 0.009]
    n = len(active_users)
    worst_case = (n * (n - 1)) // 2 if n > 1 else 0
    saved = max(0, worst_case - len(txns))

    return SimplifiedSettlementResponse(
        total_transactions_saved=saved,
        transactions=txns
    )
