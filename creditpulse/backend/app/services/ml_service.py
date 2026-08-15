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
# 3. IMPORT ML SERVICE
# ============================================================

from ml.serve import predict


# ============================================================
# 4. PUBLIC FUNCTION
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

    return predict(profile)