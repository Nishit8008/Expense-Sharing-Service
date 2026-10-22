from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="SET NULL"), nullable=True, index=True)
    payer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    payee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    payer = relationship("User", back_populates="settlements_paid", foreign_keys=[payer_id])
    payee = relationship("User", back_populates="settlements_received", foreign_keys=[payee_id])
    group = relationship("Group", back_populates="settlements")
