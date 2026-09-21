"""
Routes de demande de crédit.

Palier A.2 :
POST /credit/apply

Le router reçoit la demande, appelle le service ML
et retourne le score ainsi que l'explication SHAP.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas.credit import (
    CreditApplicationRequest,
    CreditApplicationResponse,
)
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..services.ml_service import ScoringUnavailable, predict_credit


router = APIRouter(
    prefix="/credit",
    tags=["Credit"],
)


@router.post(
    "/apply",
    response_model=CreditApplicationResponse,
)
def apply_credit(
    application: CreditApplicationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Effectue le scoring d'une demande de crédit authentifiée.
    """

    profile = {
        "revenu_mensuel": application.revenu_mensuel,
        "dettes_actuelles": application.dettes_actuelles,
        "age": application.age,
        "anciennete_emploi": application.anciennete_emploi,
        "nombre_credits_en_cours": (
            application.nombre_credits_en_cours
        ),
        "historique_paiement": (
            application.historique_paiement
        ),
    }

    try:
        result = predict_credit(profile)
    except ScoringUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return result
