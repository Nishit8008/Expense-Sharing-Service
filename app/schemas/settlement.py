from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class SettlementCreate(BaseModel):
    payer_id: int = Field(..., gt=0, description="User ID paying the money")
    payee_id: int = Field(..., gt=0, description="User ID receiving the money")
    amount: float = Field(..., gt=0, description="Settlement amount")
    group_id: Optional[int] = Field(None, gt=0, description="Optional group context")
    notes: Optional[str] = Field(None, max_length=255, description="Optional settlement notes")

    @field_validator("payee_id")
    @classmethod
    def validate_different_users(cls, v: int, info) -> int:
        if "payer_id" in info.data and v == info.data["payer_id"]:
            raise ValueError("Payer and Payee cannot be the same user")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Settlement amount must be greater than 0")
        return round(v, 2)


class SettlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payer_id: int
    payer_name: str
    payee_id: int
    payee_name: str
    amount: float
    group_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime

