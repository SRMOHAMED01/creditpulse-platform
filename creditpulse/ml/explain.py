"""
explain.py — Explicabilité SHAP (Palier A.1)

Fonctions :
1. load_model(path) -> XGBClassifier
2. get_shap_values(model, profile_df) -> shap.Explanation
3. format_explanation(shap_values, feature_names) -> list[dict]
   Retourne une liste triée par importance absolue :
   [
     {"feature": "dti_ratio", "impact": +0.32, "direction": "increases_risk"},
     {"feature": "historique_paiement", "impact": -0.21, "direction": "decreases_risk"},
     ...
   ]
"""

from pathlib import Path
from typing import List, Dict
import pandas as pd
import xgboost as xgb
from xgboost import XGBClassifier
import shap

MODEL_DIR = Path(__file__).parent / "model_registry"
MODEL_PATH = MODEL_DIR / "model.json"

FEATURE_COLUMNS = [
    "revenu_mensuel",
    "dettes_actuelles",
    "age",
    "anciennete_emploi",
    "nombre_credits_en_cours",
    "historique_paiement",
    "dti_ratio",
]


def load_model(path: Path = MODEL_PATH) -> XGBClassifier:
    """
    Charge le modèle XGBoost sauvegardé par train.py.
    """
    model = XGBClassifier()
    model.load_model(str(path))
    return model


def get_shap_values(model: XGBClassifier, profile_df: pd.DataFrame):
    """
    Calcule les valeurs SHAP pour un profil donné (DataFrame 1 ligne).
    """
    # TreeExplainer est optimisé pour les modèles d'arbres (XGBoost, LightGBM, etc.)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(profile_df[FEATURE_COLUMNS])
    return shap_values


def format_explanation(shap_values, feature_names: List[str]) -> List[Dict]:
    """
    Formate les SHAP values en liste de dicts triés par importance absolue.

    shap_values :
      - Pour XGBClassifier binaire, shap_values peut être de shape (n_samples, n_features)
        ou (n_samples, n_features, 2) selon la version / configuration.
      - Ici, on prend la colonne pour la classe 1 (défaut).
    """
    # Si shape 3D (n_samples, n_features, 2), on prend la classe 1
    if shap_values.ndim == 3:
        shap_values = shap_values[:, :, 1]

    # On prend la première (et seule) ligne
    values = shap_values[0]

    explanations = []
    for feat, val in zip(feature_names, values):
        direction = "increases_risk" if val > 0 else "decreases_risk"
        explanations.append({
            "feature": feat,
            "impact": round(float(val), 4),
            "direction": direction,
        })

    # Tri par importance absolue décroissante
    explanations.sort(key=lambda x: abs(x["impact"]), reverse=True)
    return explanations


# ============================================================
# Petit test local (optionnel)
# ============================================================

if __name__ == "__main__":
    # Exemple de profil
    profile = {
        "revenu_mensuel": 15000,
        "dettes_actuelles": 3000,
        "age": 30,
        "anciennete_emploi": 5,
        "nombre_credits_en_cours": 1,
        "historique_paiement": 0.95,
    }

    # Calcul du DTI
    profile["dti_ratio"] = round(profile["dettes_actuelles"] / profile["revenu_mensuel"], 3)

    profile_df = pd.DataFrame([profile])

    model = load_model()
    shap_vals = get_shap_values(model, profile_df)
    exp = format_explanation(shap_vals, FEATURE_COLUMNS)

    import json
    print(json.dumps(exp, indent=2, ensure_ascii=False))