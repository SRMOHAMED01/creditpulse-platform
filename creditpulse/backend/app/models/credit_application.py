"""
credit_application.py — Modèle CreditApplication
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ..database import Base


class CreditApplication(Base):
    __tablename__ = "credit_applications"
    __table_args__ = (Index("ix_credit_applications_user_created", "user_id", "created_at", "id"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_amount = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    probability_default = Column(Float, nullable=False)
    decision = Column(String, nullable=False)  # "accepté" ou "refusé"
    input_snapshot = Column(JSON, nullable=True)
    explanation = Column(JSON, nullable=True)
    model_version = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relations
    user = relationship("User", back_populates="credit_applications")
