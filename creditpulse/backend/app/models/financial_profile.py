"""
financial_profile.py — Modèle FinancialProfile
"""

from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from ..database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    revenu_mensuel = Column(Float, nullable=False)
    dettes_actuelles = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    anciennete_emploi = Column(Float, nullable=False)
    nombre_credits_en_cours = Column(Integer, nullable=False)
    historique_paiement = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relations
    user = relationship("User", back_populates="financial_profile")
