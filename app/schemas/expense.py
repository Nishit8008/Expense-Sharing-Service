from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SplitItem(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user sharing this expense")
    amount: float = Field(..., gt=0, description="Exact amount owed by this user")


class ExpenseCreate(BaseModel):
    group_id: int = Field(..., gt=0, description="Group ID where expense was incurred")
    paid_by: int = Field(..., gt=0, description="User ID of the payer")
    amount: float = Field(..., gt=0, description="Total amount paid (> 0)")
    description: str = Field(..., min_length=1, max_length=255, description="Description of the expense")
    category: Optional[str] = Field("General", max_length=50, description="Expense category (e.g., Food, Travel, Stay)")
    splits: Optional[List[SplitItem]] = Field(None, description="Optional custom splits. If omitted, split equally among all group members")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Expense description cannot be empty")
        return clean

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return round(v, 2)


class SplitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    user_name: str
    amount: float


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    amount: float
    paid_by: str  # User name as shown in assignment page 7 example
    paid_by_id: int
    category: str
    split_type: str
    created_at: datetime
    splits: List[SplitResponse] = []


# Schema strictly formatted matching the exact sample in assignment page 7:
# [{"description": "Dinner", "amount": 1200, "paid_by": "Mohit"}]
class ExpenseSimpleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    description: str
    amount: float
    paid_by: str

