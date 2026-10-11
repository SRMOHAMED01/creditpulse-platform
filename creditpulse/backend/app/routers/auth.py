"""
auth.py — Routes d'authentification (Palier A.2)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.security import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models.user import User
from ..schemas.auth import Token, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    email = user.email.lower()
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists.",
        )

    db_user = User(
        email=email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    email = user.email.lower()
    db_user = db.query(User).filter(User.email == email).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}
