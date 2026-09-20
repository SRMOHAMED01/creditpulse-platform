"""
serve.py

Point d'entrée du modèle de scoring utilisé par le backend.

Responsabilités :
1. Charger le modèle XGBoost.
2. Recevoir un profil financier.
3. Préparer les features.
4. Calculer la probabilité de défaut.
5. Transformer cette probabilité en score de crédit.
6. Déterminer la décision.
7. Générer l'explication SHAP.
"""

from functools import lru_cache

import pandas as pd

from .explain import load_model, explain_profile
from .paths import resolve_model_path


# ============================================================
# CONFIGURATION
# ============================================================



# Score minimum nécessaire pour accepter une demande
ACCEPTANCE_THRESHOLD = 60


# ============================================================
# FEATURE COLUMNS
# ============================================================

FEATURE_ORDER = [
    "revenu_mensuel",
    "dettes_actuelles",
    "age",
    "anciennete_emploi",
    "nombre_credits_en_cours",
    "historique_paiement",
]


# ============================================================
# LOAD MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_model(model_path=None):
    """
    Charge le modèle une seule fois.

    Grâce à lru_cache, le modèle n'est pas rechargé
    à chaque prédiction.
    """

    return load_model(resolve_model_path(model_path))


# ============================================================
# VALIDATE PROFILE
# ============================================================

def validate_profile(
    profile: dict,
):
    """
    Vérifie les valeurs du profil financier.
    """

    # --------------------------------------------------------
    # Required fields
    # --------------------------------------------------------

    missing_fields = [
        field
        for field in FEATURE_ORDER
        if field not in profile
    ]

    if missing_fields:
        raise ValueError(
            f"Missing fields: {missing_fields}"
        )

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    try:

        revenu = float(
            profile["revenu_mensuel"]
        )

        dettes = float(
            profile["dettes_actuelles"]
        )

        age = float(
            profile["age"]
        )

        anciennete = float(
            profile["anciennete_emploi"]
        )

        credits = float(
            profile["nombre_credits_en_cours"]
        )

        historique = float(
            profile["historique_paiement"]
        )

    except (TypeError, ValueError) as exc:

        raise ValueError(
            "All financial profile fields must be numeric."
        ) from exc

    # --------------------------------------------------------
    # Business validation
    # --------------------------------------------------------

    if revenu <= 0:
        raise ValueError(
            "revenu_mensuel must be greater than 0."
        )

    if dettes < 0:
        raise ValueError(
            "dettes_actuelles cannot be negative."
        )

    if not 18 <= age <= 100:
        raise ValueError(
            "age must be between 18 and 100."
        )

    if anciennete < 0:
        raise ValueError(
            "anciennete_emploi cannot be negative."
        )

    if credits < 0:
        raise ValueError(
            "nombre_credits_en_cours cannot be negative."
        )

    if not 0 <= historique <= 1:
        raise ValueError(
            "historique_paiement must be between 0 and 1."
        )


# ============================================================
# PREPARE PROFILE
# ============================================================

def prepare_profile(
    profile: dict,
) -> pd.DataFrame:
    """
    Transforme le dictionnaire reçu en DataFrame
    utilisable par XGBoost et SHAP.
    """

    validate_profile(profile)

    # Copie pour ne pas modifier le dictionnaire original
    data = profile.copy()

    # --------------------------------------------------------
    # Convert values
    # --------------------------------------------------------

    data["revenu_mensuel"] = float(
        data["revenu_mensuel"]
    )

    data["dettes_actuelles"] = float(
        data["dettes_actuelles"]
    )

    data["age"] = float(
        data["age"]
    )

    data["anciennete_emploi"] = float(
        data["anciennete_emploi"]
    )

    data["nombre_credits_en_cours"] = float(
        data["nombre_credits_en_cours"]
    )

    data["historique_paiement"] = float(
        data["historique_paiement"]
    )

    # --------------------------------------------------------
    # Calculate DTI
    # --------------------------------------------------------

    data["dti_ratio"] = (
        data["dettes_actuelles"]
        / data["revenu_mensuel"]
    )

    # --------------------------------------------------------
    # Create DataFrame
    # --------------------------------------------------------

    model_features = [
        data[field]
        for field in [
            "revenu_mensuel",
            "dettes_actuelles",
            "age",
            "anciennete_emploi",
            "nombre_credits_en_cours",
            "historique_paiement",
            "dti_ratio",
        ]
    ]

    profile_df = pd.DataFrame(
        [model_features],
        columns=[
            "revenu_mensuel",
            "dettes_actuelles",
            "age",
            "anciennete_emploi",
            "nombre_credits_en_cours",
            "historique_paiement",
            "dti_ratio",
        ],
    )

    return profile_df


# ============================================================
# PREDICT
# ============================================================

def predict(
    profile: dict,
    model_path=None,
) -> dict:
    """
    Effectue une prédiction de crédit.

    Returns
    -------
    dict
        {
            "score": int,
            "probability_default": float,
            "decision": str,
            "explanation": list
        }
    """

    # --------------------------------------------------------
    # 1. Load model
    # --------------------------------------------------------

    model = get_model(model_path)

    # --------------------------------------------------------
    # 2. Prepare profile
    # --------------------------------------------------------

    profile_df = prepare_profile(
        profile
    )

    # --------------------------------------------------------
    # 3. Default probability
    # --------------------------------------------------------

    probability_default = model.predict_proba(
        profile_df
    )[0][1]

    # --------------------------------------------------------
    # 4. Credit score
    # --------------------------------------------------------

    score = round(
        (1 - probability_default) * 100
    )

    score = max(
        0,
        min(100, score),
    )

    # --------------------------------------------------------
    # 5. Decision
    # --------------------------------------------------------

    if score >= ACCEPTANCE_THRESHOLD:
        decision = "accepté"
    else:
        decision = "refusé"

    # --------------------------------------------------------
    # 6. SHAP explanation
    # --------------------------------------------------------

    explanation = explain_profile(
        model,
        profile_df,
    )

    # --------------------------------------------------------
    # 7. Final result
    # --------------------------------------------------------

    return {
        "score": score,
        "probability_default": round(
            float(probability_default),
            4,
        ),
        "decision": decision,
        "explanation": explanation,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CreditPulse - Prediction Service")
    print("=" * 60)

    test_profile = {
        "revenu_mensuel": 15000,
        "dettes_actuelles": 3000,
        "age": 30,
        "anciennete_emploi": 5,
        "nombre_credits_en_cours": 1,
        "historique_paiement": 0.95,
    }

    print("\n[1/2] Customer profile:")

    for key, value in test_profile.items():
        print(
            f"  {key}: {value}"
        )

    print("\n[2/2] Prediction:")

    result = predict(
        test_profile
    )

    print(
        f"\nScore: "
        f"{result['score']}/100"
    )

    print(
        f"Probability of default: "
        f"{result['probability_default']}"
    )

    print(
        f"Decision: "
        f"{result['decision']}"
    )

    print("\nExplanation:")

    for item in result["explanation"]:

        print(
            f"  - {item['feature']}: "
            f"{item['impact']:+.4f} "
            f"({item['direction']})"
        )

    print(
        "\nPrediction completed successfully."
    )