"""
feature_store.py — Routes for the feature store (Palier B).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies.auth import get_current_user
from ..models.financial_profile import FinancialProfile
from ..models.user import User
from ..services.feature_store_service import sync_user_profile

router = APIRouter(prefix="/feature-store", tags=["feature-store"])


@router.post("/sync", status_code=status.HTTP_200_OK)
def sync_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Sync the current user's financial profile into the feature store."""
    profile = db.query(FinancialProfile).filter(
        FinancialProfile.user_id == current_user.id
    ).first()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found.",
        )

    record = sync_user_profile(
        db,
        user_id=current_user.id,
        profile_id=profile.id,
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync feature store.",
        )
    db.commit()
    return {
        "profile_id": record.profile_id,
        "user_id": record.user_id,
        "dti_ratio": record.dti_ratio,
        "score_regularite": record.score_regularite,
        "profile_updated_at": record.profile_updated_at,
    }
