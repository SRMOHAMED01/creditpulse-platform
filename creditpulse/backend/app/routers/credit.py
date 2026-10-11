"""
Routes de demande de crédit.

Palier A.2 :
POST /credit/apply

Le router reçoit la demande, appelle le service ML
et retourne le score ainsi que l'explication SHAP.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models.credit_application import CreditApplication
from ..models.user import User
from ..schemas.credit import (
    CreditApplicationRequest,
    SavedCreditApplicationResponse,
)
from ..services.ml_service import ScoringUnavailable, predict_credit

router = APIRouter(
    prefix="/credit",
    tags=["Credit"],
)


@router.post(
    "/apply",
    response_model=SavedCreditApplicationResponse,
)
def apply_credit(
    application: CreditApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    record = CreditApplication(
        user_id=current_user.id,
        requested_amount=application.requested_amount,
        duration_months=application.duration_months,
        input_snapshot=application.model_dump(),
        **result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/applications", response_model=list[SavedCreditApplicationResponse])
def list_applications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(CreditApplication)
        .filter(CreditApplication.user_id == current_user.id)
        .order_by(CreditApplication.created_at.desc(), CreditApplication.id.desc())
        .offset(offset).limit(limit).all()
    )


@router.get("/applications/{application_id}", response_model=SavedCreditApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(CreditApplication).filter(
        CreditApplication.id == application_id,
        CreditApplication.user_id == current_user.id,
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Assessment not found.")
    return record
