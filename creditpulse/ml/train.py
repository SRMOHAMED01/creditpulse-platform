"""
train.py — Entraînement du modèle de scoring crédit (Palier A.1)

À IMPLÉMENTER :
1. generate_synthetic_data(n_samples: int) -> pd.DataFrame
   Colonnes attendues : revenu_mensuel, dettes_actuelles, age,
   anciennete_emploi, nombre_credits_en_cours, historique_paiement,
   dti_ratio (dettes / revenu), defaut_paiement (0/1, cible)
   -> Utilise une logique de probabilité réaliste : plus dti_ratio est
      élevé et plus historique_paiement est mauvais, plus la proba de
      defaut_paiement=1 doit être élevée.

2. train_model(df: pd.DataFrame) -> XGBClassifier
   - train_test_split (stratifié sur la cible, la classe est déséquilibrée)
   - XGBClassifier avec early stopping
   - Évaluer avec roc_auc_score, precision_score, recall_score, f1_score
     (PAS seulement accuracy : en credit scoring le déséquilibre de
     classes rend l'accuracy trompeuse)

3. log_to_mlflow(model, params, metrics) — Palier D
   - mlflow.start_run()
   - mlflow.log_params(...) / mlflow.log_metrics(...)
   - mlflow.xgboost.log_model(model, "model")

4. save_model(model, path="model_registry/model.json")

if __name__ == "__main__":
    # Enchaîner les 4 étapes ci-dessus
    pass
