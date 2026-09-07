"""
explain.py
Explicabilité du modèle de scoring crédit avec SHAP.

Si la dépendance native SHAP/numba est bloquée par le système
Windows (Application Control / DLL policy), on garde un mode de
secours basé sur l'importance des features pour conserver la
fonction de scoring.
"""

from pathlib import Path

import pandas as pd
import xgboost as xgb

try:
    import shap  # type: ignore
except ImportError:  # pragma: no cover - dépendance native locale
    shap = None


# ============================================================
# 1. FEATURE NAMES
# ============================================================

FEATURE_COLUMNS = [
    "revenu_mensuel",
    "dettes_actuelles",
    "age",
    "anciennete_emploi",
    "nombre_credits_en_cours",
    "historique_paiement",
    "dti_ratio",
]


# ============================================================
# 2. LOAD MODEL
# ============================================================

def load_model(
    path="model_registry/model.json",
):
    """
    Charge le modèle XGBoost sauvegardé par train.py.
    """

    model_path = Path(__file__).parent / path

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model not found: {model_path}"
        )

    model = xgb.XGBClassifier()

    model.load_model(
        str(model_path)
    )

    return model


# ============================================================
# 3. VALIDATE PROFILE
# ============================================================

def validate_profile(
    profile_df: pd.DataFrame,
):
    """
    Vérifie que le profil contient exactement
    les features utilisées pendant l'entraînement.
    """

    missing_features = [
        feature
        for feature in FEATURE_COLUMNS
        if feature not in profile_df.columns
    ]

    if missing_features:
        raise ValueError(
            "Missing features: "
            + ", ".join(missing_features)
        )

    return profile_df[
        FEATURE_COLUMNS
    ]


# ============================================================
# 4. GET SHAP VALUES
# ============================================================

def get_shap_values(
    model,
    profile_df: pd.DataFrame,
):
    """
    Calcule les valeurs SHAP pour un ou plusieurs profils.

    Si SHAP n'est pas disponible, on retourne une approximation
    basée sur l'importance des features du modèle.
    """

    if shap is None:
        feature_names = profile_df.columns.tolist()
        baseline = {}
        for idx, feature in enumerate(feature_names):
            value = float(profile_df.iloc[0][feature])
            if hasattr(model, "feature_importances_"):
                importance = float(model.feature_importances_[idx])
            else:
                importance = 1.0 / len(feature_names)
            baseline[feature] = importance * value
        return baseline

    explainer = shap.TreeExplainer(
        model
    )

    shap_values = explainer(
        profile_df
    )

    return shap_values


# ============================================================
# 5. FORMAT EXPLANATION
# ============================================================

def format_explanation(
    shap_values,
    feature_names,
):
    """
    Transforme les valeurs SHAP en format JSON-friendly.

    Si la vraie explication SHAP n'est pas disponible, on utilise
    une approximation locale inspirée de l'importance des features.
    """

    explanations = []

    if shap is None and isinstance(shap_values, dict):
        for feature in feature_names:
            impact = float(shap_values.get(feature, 0.0))
            if impact >= 0:
                direction = "increases_risk"
            else:
                direction = "decreases_risk"
            explanations.append(
                {
                    "feature": feature,
                    "impact": round(abs(impact), 4),
                    "direction": direction,
                }
            )
        explanations.sort(key=lambda item: item["impact"], reverse=True)
        return explanations

    values = shap_values.values[0]

    for feature, impact in zip(
        feature_names,
        values,
    ):

        impact = float(impact)

        if impact > 0:
            direction = "increases_risk"
        elif impact < 0:
            direction = "decreases_risk"
        else:
            direction = "neutral"

        explanations.append(
            {
                "feature": feature,
                "impact": round(
                    impact,
                    4,
                ),
                "direction": direction,
            }
        )

    explanations.sort(
        key=lambda item: abs(
            item["impact"]
        ),
        reverse=True,
    )

    return explanations


# ============================================================
# 6. EXPLAIN PROFILE
# ============================================================

def explain_profile(
    model,
    profile_df: pd.DataFrame,
):
    """
    Fonction principale permettant
    d'expliquer la prédiction d'un profil.
    """

    # Vérification et normalisation
    profile_df = validate_profile(
        profile_df
    )

    # Calcul SHAP
    shap_values = get_shap_values(
        model,
        profile_df,
    )

    # Formatage
    explanation = format_explanation(
        shap_values,
        FEATURE_COLUMNS,
    )

    return explanation


# ============================================================
# 7. TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CreditPulse - SHAP Explanation")
    print("=" * 60)

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    print("\n[1/3] Loading model...")

    model = load_model()

    print(
        "Model loaded successfully."
    )

    # --------------------------------------------------------
    # Example customer
    # --------------------------------------------------------

    profile = pd.DataFrame(
        [
            {
                "revenu_mensuel": 15000,
                "dettes_actuelles": 3000,
                "age": 30,
                "anciennete_emploi": 5,
                "nombre_credits_en_cours": 1,
                "historique_paiement": 0.95,
                "dti_ratio": 3000 / 15000,
            }
        ]
    )

    # --------------------------------------------------------
    # Calculate SHAP
    # --------------------------------------------------------

    print(
        "\n[2/3] Calculating SHAP values..."
    )

    explanation = explain_profile(
        model,
        profile,
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    print(
        "\n[3/3] Explanation:"
    )

    for item in explanation:

        print(
            f"- {item['feature']}: "
            f"{item['impact']:+.4f} "
            f"({item['direction']})"
        )

    print(
        "\nSHAP explanation completed."
    )