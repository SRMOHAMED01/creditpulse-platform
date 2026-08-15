"""
Routes de demande de crédit.

Palier A.2 :
POST /credit/apply

Le router reçoit la demande, appelle le service ML
et retourne le score ainsi que l'explication SHAP.
"""

from fastapi import APIRouter

from ..schemas.credit import (
    CreditApplicationRequest,
    CreditApplicationResponse,
)

from ..services.ml_service import predict_credit


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
):
    """
    Effectue le scoring d'une demande de crédit.
    """

    # Transformer le modèle Pydantic en dictionnaire
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

    # Appel du moteur ML
    result = predict_credit(profile)

    return result