from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    group_memberships = relationship("GroupMember", back_populates="user", cascade="all, delete-orphan")
    expenses_paid = relationship("Expense", back_populates="payer", foreign_keys="Expense.paid_by")
    splits = relationship("ExpenseSplit", back_populates="user", cascade="all, delete-orphan")
    settlements_paid = relationship("Settlement", back_populates="payer", foreign_keys="Settlement.payer_id")
    settlements_received = relationship("Settlement", back_populates="payee", foreign_keys="Settlement.payee_id")
