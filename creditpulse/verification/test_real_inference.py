"""Native inference checks: intentionally fail if the runtime/model cannot load."""
import math

import pytest

from ml.explain import FEATURE_COLUMNS
from ml.serve import get_model, predict, prepare_profile

PROFILE = {
    "revenu_mensuel": 15000, "dettes_actuelles": 3000, "age": 30,
    "anciennete_emploi": 5, "nombre_credits_en_cours": 1,
    "historique_paiement": 0.95,
}


def test_genuine_prediction_has_valid_score_version_and_signed_explanation():
    result = predict(PROFILE)
    assert 0 <= result["probability_default"] <= 1
    assert 0 <= result["score"] <= 100
    assert result["decision"] in ("accepté", "refusé")
    assert len(result["model_version"]) == 64
    int(result["model_version"], 16)
    assert {item["feature"] for item in result["explanation"]} == set(FEATURE_COLUMNS)
    for item in result["explanation"]:
        assert math.isfinite(item["impact"])
        expected = "increases_risk" if item["impact"] > 0 else "decreases_risk" if item["impact"] < 0 else "neutral"
        # Formatting rounds very small contributions to zero, retaining their original direction.
        if item["impact"] != 0:
            assert item["direction"] == expected


def test_native_shap_contributions_reconstruct_model_margin():
    import xgboost as xgb

    booster = get_model()
    matrix = xgb.DMatrix(prepare_profile(PROFILE), feature_names=FEATURE_COLUMNS)
    contributions = booster.predict(matrix, pred_contribs=True)[0]
    margin = float(booster.predict(matrix, output_margin=True)[0])
    assert float(contributions.sum()) == pytest.approx(margin, abs=1e-5)
