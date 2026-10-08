"""Load XGBoost artifacts and return genuine signed SHAP explanations."""
import pandas as pd
import xgboost as xgb
from .paths import resolve_model_path

FEATURE_COLUMNS = [
    "revenu_mensuel", "dettes_actuelles", "age", "anciennete_emploi",
    "nombre_credits_en_cours", "historique_paiement", "dti_ratio",
]

def load_model(path=None):
    model_path = resolve_model_path(path)
    if not model_path.is_file():
        raise FileNotFoundError(f"Model not found: {model_path}. Run python -m ml.train or configure MODEL_PATH.")
    # Serving needs only the native runtime, not optional sklearn/plotting imports.
    model = xgb.Booster()
    try:
        model.load_model(str(model_path))
    except (xgb.core.XGBoostError, ValueError) as exc:
        raise RuntimeError(f"Cannot load XGBoost model: {model_path}") from exc
    if model.feature_names != FEATURE_COLUMNS:
        raise ValueError("Model feature names/order do not match CreditPulse. Train a compatible model.")
    return model

def validate_profile(profile_df: pd.DataFrame):
    missing = [name for name in FEATURE_COLUMNS if name not in profile_df.columns]
    if missing:
        raise ValueError("Missing features: " + ", ".join(missing))
    return profile_df[FEATURE_COLUMNS]

def get_shap_values(model, profile_df):
    """Use XGBoost's native TreeSHAP implementation for online inference."""
    matrix = xgb.DMatrix(profile_df, feature_names=FEATURE_COLUMNS)
    # The final contribution is the model bias; the API explains input features.
    return model.predict(matrix, pred_contribs=True)[0][:-1]

def format_explanation(shap_values, feature_names):
    explanations = []
    for feature, raw in zip(feature_names, shap_values):
        impact = float(raw)
        direction = "increases_risk" if impact > 0 else "decreases_risk" if impact < 0 else "neutral"
        explanations.append({"feature": feature, "impact": round(impact, 4), "direction": direction})
    return sorted(explanations, key=lambda item: abs(item["impact"]), reverse=True)

def explain_profile(model, profile_df):
    return format_explanation(get_shap_values(model, validate_profile(profile_df)), FEATURE_COLUMNS)
