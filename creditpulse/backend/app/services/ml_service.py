"""
ml_service.py

Pont entre le backend FastAPI et le moteur ML.

Le backend utilise la fonction predict() définie dans
ml/serve.py au lieu de manipuler directement XGBoost
ou SHAP.
"""

import sys
from pathlib import Path


# ============================================================
# 1. FIND PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ============================================================
# 2. ADD PROJECT ROOT TO PYTHON PATH
# ============================================================

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


# ============================================================
# 3. PUBLIC FUNCTION
# ============================================================

def predict_credit(profile: dict) -> dict:
    """
    Effectue une prédiction de crédit.

    Parameters
    ----------
    profile : dict
        Profil financier du client.

    Returns
    -------
    dict
        Résultat du modèle contenant :

        - score
        - probability_default
        - decision
        - explanation
    """
    try:
        from ml.serve import predict
    except ModuleNotFoundError as exc:
        raise ImportError(
            "ML dependencies are not installed. Install the ML stack from ml/requirements.txt "
            "before calling the credit scoring endpoint."
        ) from exc

    return predict(profile)