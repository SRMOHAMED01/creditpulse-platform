"""
explain.py
Explicabilité du modèle de scoring crédit avec SHAP.
"""

from pathlib import Path

import pandas as pd
import shap
import xgboost as xgb


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

def load_model(path="model_registry/model.json"):
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
# 3. GET SHAP VALUES
# ============================================================

def get_shap_values(
    model,
    profile_df: pd.DataFrame,
):
    """
    Calcule les valeurs SHAP pour un ou plusieurs profils.

    TreeExplainer est utilisé car notre modèle est basé
    sur XGBoost et donc sur des arbres de décision.
    """

    explainer = shap.TreeExplainer(model)

    shap_values = explainer(
        profile_df
    )

    return shap_values


# ============================================================
# 4. FORMAT EXPLANATION
# ============================================================

def format_explanation(
    shap_values,
    feature_names,
):
    """
    Transforme les valeurs SHAP en format JSON-friendly.

    Retourne une liste triée par importance absolue.
    """

    values = shap_values.values[0]

    explanations = []

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
                "impact": round(impact, 4),
                "direction": direction,
            }
        )

    # Les variables avec le plus grand impact
    # apparaissent en premier.
    explanations.sort(
        key=lambda item: abs(item["impact"]),
        reverse=True,
    )

    return explanations


# ============================================================
# 5. EXPLAIN PROFILE
# ============================================================

def explain_profile(
    model,
    profile_df: pd.DataFrame,
):
    """
    Fonction principale permettant d'expliquer
    la prédiction d'un profil.
    """

    shap_values = get_shap_values(
        model,
        profile_df,
    )

    explanation = format_explanation(
        shap_values,
        profile_df.columns.tolist(),
    )

    return explanation


# ============================================================
# 6. TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("CreditPulse - SHAP Explanation")
    print("=" * 60)

    print("\n[1/3] Loading model...")

    model = load_model()

    print("Model loaded successfully.")

    # Exemple de client
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

    print("\n[2/3] Calculating SHAP values...")

    explanation = explain_profile(
        model,
        profile,
    )

    print("\n[3/3] Explanation:")

    for item in explanation:

        print(
            f"- {item['feature']}: "
            f"{item['impact']:+.4f} "
            f"({item['direction']})"
        )

    print("\nSHAP explanation completed.")