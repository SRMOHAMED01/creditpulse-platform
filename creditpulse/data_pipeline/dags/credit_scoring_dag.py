"""
credit_scoring_dag.py — DAG Airflow principal (Palier B.4)

À IMPLÉMENTER : DAG avec les tâches suivantes, dans l'ordre :
1. extract_new_profiles       : lit les nouveaux financial_profiles depuis PostgreSQL
2. validate_raw_data           : Great Expectations (data_pipeline/great_expectations/)
3. run_dbt_models                : déclenche `dbt run` (data_pipeline/dbt_project/)
4. write_to_feature_store          : écrit le résultat dans la table feature_store
5. (Palier D) check_drift_and_retrain : appelle ml/monitor.py, déclenche
   ml/train.py si un drift est détecté

Utiliser PythonOperator ou BashOperator selon les tâches.
schedule_interval : toutes les heures ou en trigger manuel selon ton besoin de démo.
"""
