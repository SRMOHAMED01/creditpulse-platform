"""Feature-engineering utilities for the Palier B pipeline."""

from __future__ import annotations

from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def compute_feature_row(profile: dict[str, Any]) -> dict[str, Any]:
    """Transform raw profile data into model-ready features used by the feature store."""
    revenu = _safe_float(profile.get("revenu_mensuel"))
    dettes = _safe_float(profile.get("dettes_actuelles"))
    historique = _safe_float(profile.get("historique_paiement"), default=0.0)

    dti_ratio = round(dettes / revenu, 3) if revenu > 0 else 0.0
    score_regularite = max(0.0, min(1.0, historique))

    row = {
        "profile_id": profile.get("profile_id"),
        "user_id": profile.get("user_id"),
        "revenu_mensuel": float(revenu),
        "dettes_actuelles": float(dettes),
        "age": profile.get("age"),
        "anciennete_emploi": profile.get("anciennete_emploi"),
        "nombre_credits_en_cours": profile.get("nombre_credits_en_cours"),
        "historique_paiement": float(historique),
        "dti_ratio": float(dti_ratio),
        "score_regularite": float(score_regularite),
    }
    return row


def build_feature_store_rows(profiles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [compute_feature_row(profile) for profile in profiles]
