"""
feature_store.py — Modèle FeatureStore (Table dbt)
"""

from sqlalchemy import Column, Integer, Float, DateTime
from ..database import Base

class FeatureStore(Base):
    __tablename__ = "feature_store"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    revenu_mensuel = Column(Float, nullable=False)
    dettes_actuelles = Column(Float, nullable=False)
    age = Column(Integer, nullable=False)
    anciennete_emploi = Column(Float, nullable=False)
    nombre_credits_en_cours = Column(Integer, nullable=False)
    historique_paiement = Column(Float, nullable=False)
    dti_ratio = Column(Float, nullable=False)
    score_regularite = Column(Float, nullable=True)
    profile_updated_at = Column(DateTime, nullable=True)
