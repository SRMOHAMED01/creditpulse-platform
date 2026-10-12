"""
Routes de demande de crédit.

Palier A.2 :
POST /credit/apply — scoring synchrone

Palier C.1 :
POST /credit/apply-async — publie un événement Kafka, scoring asynchrone
GET /credit/status/{id} — polling pour le résultat asynchrone
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import case, func
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

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/credit",
    tags=["Credit"],
)


def _profile_from_request(application: CreditApplicationRequest) -> dict:
    return {
        "revenu_mensuel": application.revenu_mensuel,
        "dettes_actuelles": application.dettes_actuelles,
        "age": application.age,
        "anciennete_emploi": application.anciennete_emploi,
        "nombre_credits_en_cours": application.nombre_credits_en_cours,
        "historique_paiement": application.historique_paiement,
    }


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
    Effectue le scoring d'une demande de crédit authentifiée (synchrone).
    """
    profile = _profile_from_request(application)

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
        status="completed",
        **result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post(
    "/apply-async",
    response_model=SavedCreditApplicationResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def apply_credit_async(
    application: CreditApplicationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Publie une demande de crédit dans Kafka pour traitement asynchrone (Palier C).

    Crée un enregistrement avec status 'pending' puis publie l'événement.
    Le client poll GET /credit/applications/{id} ou /credit/status/{id}.
    """
    profile = _profile_from_request(application)

    record = CreditApplication(
        user_id=current_user.id,
        requested_amount=application.requested_amount,
        duration_months=application.duration_months,
        input_snapshot=application.model_dump(),
        status="pending",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    try:
        from ..kafka.producer import publish_credit_request

        publish_credit_request(
            application_id=record.id,
            user_id=current_user.id,
            profile=profile,
        )
        logger.info("Credit request %d published to Kafka", record.id)
    except Exception as exc:
        logger.error("Failed to publish Kafka event for application %d: %s", record.id, exc)
        # The consumer may still pick it up if running; otherwise the
        # application stays pending and can be retried.
        record.status = "pending_error"
        db.commit()
        db.refresh(record)

    return record


@router.get("/status/{application_id}", response_model=SavedCreditApplicationResponse,
            responses={
                200: {"description": "Application status (may be pending or scored)."},
                404: {"description": "Application not found."},
            })
def get_application_status(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retourne le statut d'une demande de crédit (synchrone ou asynchrone)."""
    record = db.query(CreditApplication).filter(
        CreditApplication.id == application_id,
        CreditApplication.user_id == current_user.id,
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Application not found.")
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
        raise HTTPException(status_code=404, detail="Application not found.")
    return record


@router.get("/stats", response_model=dict)
def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retourne des statistiques de scoring pour l'utilisateur courant."""
    stats = (
        db.query(
            func.count(CreditApplication.id).label("total"),
            func.round(func.avg(CreditApplication.score), 2).label("avg_score"),
            func.sum(case((CreditApplication.decision == "accepté", 1), else_=0)).label("accepted"),
        )
        .filter(CreditApplication.user_id == current_user.id)
        .first()
        ._asdict()
    )
    return stats
