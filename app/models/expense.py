from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False, index=True)
    paid_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False, default="General")
    split_type = Column(String(20), nullable=False, default="EQUAL")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    group = relationship("Group", back_populates="expenses")
    payer = relationship("User", back_populates="expenses_paid", foreign_keys=[paid_by])
    splits = relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    expense_id = Column(Integer, ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("expense_id", "user_id", name="uq_expense_user"),
    )

    expense = relationship("Expense", back_populates="splits")
    user = relationship("User", back_populates="splits")
