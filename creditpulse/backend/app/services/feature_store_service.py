"""
feature_store_service.py — Writes computed features into the feature_store table.

Used by the Palier B pipeline (dbt/Airflow) and optionally by the API to keep
the feature store in sync when a user updates their financial profile.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.feature_store import FeatureStore
from .feature_pipeline import compute_feature_row

logger = logging.getLogger(__name__)


def upsert_feature_row(
    db: Session,
    profile: dict[str, Any],
) -> FeatureStore | None:
    """Insert or update a feature_store row for the given profile.

    Returns the FeatureStore record, or None if the profile is invalid.
    """
    try:
        row = compute_feature_row(profile)
    except Exception:
        logger.exception("Failed to compute feature row")
        return None

    profile_id = row.get("profile_id")
    user_id = row.get("user_id")
    if profile_id is None or user_id is None:
        logger.error("profile_id and user_id are required for feature store upsert")
        return None

    existing = db.execute(
        select(FeatureStore).filter(FeatureStore.profile_id == profile_id)
    ).scalar_one_or_none()

    now = datetime.now(UTC)
    if existing:
        for key, value in row.items():
            if key in ("profile_id", "user_id"):
                continue
            setattr(existing, key, value)
        existing.profile_updated_at = now
        db.flush()
        return existing

    record = FeatureStore(
        profile_id=profile_id,
        user_id=user_id,
        revenu_mensuel=row["revenu_mensuel"],
        dettes_actuelles=row["dettes_actuelles"],
        age=row["age"],
        anciennete_emploi=row["anciennete_emploi"],
        nombre_credits_en_cours=row["nombre_credits_en_cours"],
        historique_paiement=row["historique_paiement"],
        dti_ratio=row["dti_ratio"],
        score_regularite=row["score_regularite"],
        profile_updated_at=now,
    )
    db.add(record)
    db.flush()
    return record


def sync_user_profile(
    db: Session,
    user_id: int,
    profile_id: int,
) -> FeatureStore | None:
    """Sync a user's financial profile into the feature store."""
    from ..models.financial_profile import FinancialProfile

    profile = db.execute(
        select(FinancialProfile).filter(FinancialProfile.user_id == user_id)
    ).scalar_one_or_none()
    if profile is None:
        return None

    return upsert_feature_row(
        db,
        {
            "profile_id": profile_id,
            "user_id": user_id,
            "revenu_mensuel": profile.revenu_mensuel,
            "dettes_actuelles": profile.dettes_actuelles,
            "age": profile.age,
            "anciennete_emploi": profile.anciennete_emploi,
            "nombre_credits_en_cours": profile.nombre_credits_en_cours,
            "historique_paiement": profile.historique_paiement,
        },
    )
