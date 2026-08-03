"""
monitor.py — Détection de dérive avec Evidently AI (Palier D)

À IMPLÉMENTER :
1. load_reference_data() -> le dataset d'entraînement (train.py)
2. load_production_data() -> les données récentes du feature_store (PostgreSQL)
3. run_drift_report(reference_df, production_df) -> Report Evidently
   - Utiliser evidently.report.Report avec DataDriftPreset
   - Calculer le PSI (Population Stability Index) par feature
4. should_retrain(report) -> bool
   - True si PSI > 0.2 sur au moins une feature critique (ex: dti_ratio)

# NOTE : appelé par une tâche Airflow (data_pipeline/dags/) qui déclenche
# train.py automatiquement si should_retrain() renvoie True.
