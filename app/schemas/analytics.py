from typing import List, Dict, Optional
from pydantic import BaseModel


class CategorySpend(BaseModel):
    category: str
    amount: float
    percentage: float
    expense_count: int


class UserSpend(BaseModel):
    user_id: int
    user_name: str
    total_paid: float
    total_share: float
    net_balance: float


class GroupAnalyticsResponse(BaseModel):
    group_id: int
    group_name: str
    total_group_spending: float
    total_expenses_count: int
    category_breakdown: List[CategorySpend]
    member_spending: List[UserSpend]
    top_spender: Optional[str] = None


class SimplifiedTransaction(BaseModel):
    from_user: str
    from_user_id: int
    to_user: str
    to_user_id: int
    amount: float


class SimplifiedSettlementResponse(BaseModel):
    total_transactions_saved: int
    transactions: List[SimplifiedTransaction]
