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

from .explain import (
    load_model,
    explain_profile,
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_PATH = "model_registry/model.json"

# Score minimum nécessaire pour accepter une demande
ACCEPTANCE_THRESHOLD = 60


# ============================================================
# LOAD MODEL
# ============================================================

@lru_cache(maxsize=1)
def get_model():
    """
    Charge le modèle une seule fois.

    Grâce à lru_cache, le modèle ne sera pas rechargé
    à chaque prédiction.
    """

    return load_model(MODEL_PATH)


# ============================================================
# PREPARE PROFILE
# ============================================================

def prepare_profile(profile: dict) -> pd.DataFrame:
    """
    Transforme le dictionnaire reçu en DataFrame
    utilisable par XGBoost et SHAP.
    """

    required_fields = [
        "revenu_mensuel",
        "dettes_actuelles",
        "age",
        "anciennete_emploi",
        "nombre_credits_en_cours",
        "historique_paiement",
    ]

    # Vérification des champs obligatoires
    missing_fields = [
        field
        for field in required_fields
        if field not in profile
    ]

    if missing_fields:
        raise ValueError(
            f"Missing fields: {missing_fields}"
        )

    # Copie pour ne pas modifier le dictionnaire
    # original envoyé par l'utilisateur.
    data = profile.copy()

    # --------------------------------------------------------
    # Calcul du DTI
    # --------------------------------------------------------

    revenu = float(
        data["revenu_mensuel"]
    )

    dettes = float(
        data["dettes_actuelles"]
    )

    if revenu <= 0:
        raise ValueError(
            "revenu_mensuel must be greater than 0"
        )

    data["dti_ratio"] = (
        dettes / revenu
    )

    # --------------------------------------------------------
    # Création du DataFrame
    # --------------------------------------------------------

    feature_order = [
        "revenu_mensuel",
        "dettes_actuelles",
        "age",
        "anciennete_emploi",
        "nombre_credits_en_cours",
        "historique_paiement",
        "dti_ratio",
    ]

    profile_df = pd.DataFrame(
        [[data[field] for field in feature_order]],
        columns=feature_order,
    )

    return profile_df


# ============================================================
# PREDICT
# ============================================================

def predict(profile: dict) -> dict:
    """
    Effectue une prédiction de crédit.

    Paramètre
    ---------
    profile : dict
        Profil financier du client.

    Retour
    ------
    dict
        {
            "score": int,
            "probability_default": float,
            "decision": str,
            "explanation": list
        }
    """

    # --------------------------------------------------------
    # 1. Charger le modèle
    # --------------------------------------------------------

    model = get_model()

    # --------------------------------------------------------
    # 2. Préparer le profil
    # --------------------------------------------------------

    profile_df = prepare_profile(
        profile
    )

    # --------------------------------------------------------
    # 3. Probabilité de défaut
    # --------------------------------------------------------

    probability_default = model.predict_proba(
        profile_df
    )[0][1]

    # --------------------------------------------------------
    # 4. Calcul du score
    # --------------------------------------------------------

    score = round(
        (1 - probability_default) * 100
    )

    # Limiter le score entre 0 et 100
    score = max(
        0,
        min(100, score)
    )

    # --------------------------------------------------------
    # 5. Décision
    # --------------------------------------------------------

    if score >= ACCEPTANCE_THRESHOLD:
        decision = "accepté"
    else:
        decision = "refusé"

    # --------------------------------------------------------
    # 6. Explication SHAP
    # --------------------------------------------------------

    explanation = explain_profile(
        model,
        profile_df,
    )

    # --------------------------------------------------------
    # 7. Résultat final
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
        print(f"  {key}: {value}")

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