from app.services.feature_pipeline import compute_feature_row


def test_compute_feature_row_builds_model_ready_values():
    profile = {
        "profile_id": 101,
        "user_id": 7,
        "revenu_mensuel": 5000,
        "dettes_actuelles": 1200,
        "age": 32,
        "anciennete_emploi": 6,
        "nombre_credits_en_cours": 2,
        "historique_paiement": 0.8,
    }

    result = compute_feature_row(profile)

    assert result["profile_id"] == 101
    assert result["user_id"] == 7
    assert result["revenu_mensuel"] == 5000.0
    assert result["dettes_actuelles"] == 1200.0
    assert result["dti_ratio"] == 0.24
    assert result["score_regularite"] == 0.8
