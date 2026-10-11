"""
user.py — Modèle User
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relations
    financial_profile = relationship("FinancialProfile", back_populates="user", uselist=False)
    credit_applications = relationship("CreditApplication", back_populates="user")
