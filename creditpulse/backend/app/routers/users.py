"""
users.py — Routes utilisateur (Palier A.2)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..core.security import decode_access_token
from ..database import get_db
from ..models.financial_profile import FinancialProfile
from ..models.user import User
from ..schemas.users import FinancialProfileCreate, FinancialProfileResponse, UserMeResponse


router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


@router.get("/me", response_model=UserMeResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/profile", response_model=FinancialProfileResponse)
def save_profile(
    profile: FinancialProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing_profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        for field, value in profile.model_dump().items():
            setattr(existing_profile, field, value)
        db.commit()
        db.refresh(existing_profile)
        return existing_profile

    new_profile = FinancialProfile(
        user_id=current_user.id,
        revenu_mensuel=profile.revenu_mensuel,
        dettes_actuelles=profile.dettes_actuelles,
        age=profile.age,
        anciennete_emploi=profile.anciennete_emploi,
        nombre_credits_en_cours=profile.nombre_credits_en_cours,
        historique_paiement=profile.historique_paiement,
    )
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    return new_profile


@router.get("/profile", response_model=FinancialProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = (
        db.query(FinancialProfile)
        .filter(FinancialProfile.user_id == current_user.id)
        .first()
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Financial profile not found.",
        )
    return profile
