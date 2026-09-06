"""
auth.py — Schémas Pydantic pour auth (validation requêtes/réponses) (Palier A.2)
"""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True,
    }
