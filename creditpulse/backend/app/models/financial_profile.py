"""
financial_profile.py — Modèle FinancialProfile
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="financial_profile")