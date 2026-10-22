from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator


class GroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150, description="Name of the group")
    description: Optional[str] = Field(None, max_length=255, description="Optional description of the group")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Group name cannot be empty")
        return clean


class GroupCreate(GroupBase):
    pass


class GroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None


class GroupMemberAdd(BaseModel):
    user_id: int = Field(..., gt=0, description="ID of the user to add to the group")
    group_id: Optional[int] = Field(None, gt=0, description="Optional group ID if passed in body")


class GroupMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    joined_at: Optional[datetime] = None


class GroupDetailResponse(GroupResponse):
    members: List[GroupMemberResponse] = []

