"""
credit_application.py — Modèle CreditApplication
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class CreditApplication(Base):
    __tablename__ = "credit_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_amount = Column(Float, nullable=False)
    duration_months = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)
    probability_default = Column(Float, nullable=False)
    decision = Column(String, nullable=False)  # "accepté" ou "refusé"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="credit_applications")