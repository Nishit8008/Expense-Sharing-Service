from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = relationship("Settlement", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="group_memberships")
