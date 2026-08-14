"""
serve.py — Point d'entrée utilisé par le backend (Palier A.2, puis C)

Fonction :
def predict(profile: dict) -> dict:
    profile : dict avec les mêmes clés que les features d'entraînement
    retourne :
    {
        "score": int (0-100, probabilité de remboursement),
        "decision": "accepté" | "refusé",
        "probability_default": float,
        "explanation": [...]  # sortie de explain.format_explanation()
    }
"""

from pathlib import Path
from typing import Dict, Any
import pandas as pd
import xgboost as xgb
from xgboost import XGBClassifier

import explain

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

DECISION_THRESHOLD = 60

_model_cache = None


def _load_model() -> XGBClassifier:
    global _model_cache
    if _model_cache is None:
        _model_cache = explain.load_model(MODEL_PATH)
    return _model_cache


def predict(profile: Dict[str, Any]) -> Dict[str, Any]:
    model = _load_model()

    if "dti_ratio" not in profile:
        profile["dti_ratio"] = round(
            profile["dettes_actuelles"] / profile["revenu_mensuel"],
            3,
        )

    profile_df = pd.DataFrame([profile])
    proba_defaut = float(model.predict_proba(profile_df[FEATURE_COLUMNS])[0, 1])
    score = round((1.0 - proba_defaut) * 100)
    decision = "accepté" if score >= DECISION_THRESHOLD else "refusé"

    shap_vals = explain.get_shap_values(model, profile_df)
    explanation = explain.format_explanation(shap_vals, FEATURE_COLUMNS)

    return {
        "score": score,
        "decision": decision,
        "probability_default": round(proba_defaut, 4),
        "explanation": explanation,
    }


if __name__ == "__main__":
    import json

    profile_test = {
        "revenu_mensuel": 15000,
        "dettes_actuelles": 3000,
        "age": 30,
        "anciennete_emploi": 5,
        "nombre_credits_en_cours": 1,
        "historique_paiement": 0.95,
    }

    result = predict(profile_test)
    print(json.dumps(result, indent=2, ensure_ascii=False))