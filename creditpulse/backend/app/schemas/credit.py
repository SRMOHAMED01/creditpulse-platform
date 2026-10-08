"""
Schémas Pydantic pour les demandes de crédit.
"""

from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict, field_validator


class CreditApplicationRequest(BaseModel):
    """
    Données envoyées par le client pour demander un crédit.
    """

    revenu_mensuel: float = Field(gt=0)
    dettes_actuelles: float = Field(ge=0)
    age: int = Field(gt=18, le=100)
    anciennete_emploi: float = Field(ge=0)
    nombre_credits_en_cours: int = Field(ge=0)
    historique_paiement: float = Field(
        ge=0,
        le=1,
    )

    requested_amount: float = Field(gt=0)
    duration_months: int = Field(
        gt=0,
        le=360,
    )


class CreditApplicationResponse(BaseModel):
    """
    Résultat retourné après le scoring.
    """

    score: int
    probability_default: float
    decision: str
    explanation: list[dict]


class SavedCreditApplicationResponse(CreditApplicationResponse):
    model_config = ConfigDict(from_attributes=True)

    id: int
    requested_amount: float
    duration_months: int
    created_at: datetime
    input_snapshot: dict | None = None
    explanation: list[dict] | None = None
    model_version: str | None = None

    @field_validator("created_at")
    @classmethod
    def timestamp_with_timezone(cls, value):
        # Stored timestamps (including legacy rows) use UTC.
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value
