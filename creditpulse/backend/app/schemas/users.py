"""
users.py — Schémas Pydantic pour users (validation requêtes/réponses) (Palier A.2)
"""

from pydantic import BaseModel, Field


class FinancialProfileCreate(BaseModel):
    revenu_mensuel: float = Field(gt=0)
    dettes_actuelles: float = Field(ge=0)
    age: int = Field(gt=18, le=100)
    anciennete_emploi: float = Field(ge=0)
    nombre_credits_en_cours: int = Field(ge=0)
    historique_paiement: float = Field(ge=0, le=1)


class FinancialProfileResponse(FinancialProfileCreate):
    id: int
    user_id: int

    model_config = {
        "from_attributes": True,
    }


class UserMeResponse(BaseModel):
    id: int
    email: str

    model_config = {
        "from_attributes": True,
    }
