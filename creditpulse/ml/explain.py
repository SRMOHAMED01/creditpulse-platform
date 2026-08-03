"""
explain.py — Explicabilité SHAP (Palier A.1)

À IMPLÉMENTER :
1. load_model(path) -> charge le modèle XGBoost sauvegardé par train.py
2. get_shap_values(model, profile_df) -> shap.Explanation
   - Utiliser shap.TreeExplainer(model) car XGBoost est un modèle d'arbres
3. format_explanation(shap_values, feature_names) -> list[dict]
   Retourne une liste triée par importance absolue, ex :
   [
     {"feature": "dti_ratio", "impact": +0.32, "direction": "increases_risk"},
     {"feature": "anciennete_emploi", "impact": -0.10, "direction": "decreases_risk"},
     ...
   ]
   -> C'est ce format JSON que le frontend affichera comme graphique SHAP.
"""
