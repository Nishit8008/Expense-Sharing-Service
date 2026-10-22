from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the user")
    email: Optional[str] = Field(None, description="Optional email address")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Name cannot be empty or whitespace only")
        return clean


class UserCreate(UserBase):
    pass


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: Optional[str] = None
    created_at: Optional[datetime] = None

