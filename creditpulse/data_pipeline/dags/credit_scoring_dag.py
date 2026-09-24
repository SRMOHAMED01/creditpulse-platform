"""
credit_scoring_dag.py — DAG Airflow principal (Palier B.4)

Orchestre le pipeline de données :
1. Validation des données brutes (Great Expectations)
2. Transformation et Feature Store (dbt)
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'credit_scoring_pipeline',
    default_args=default_args,
    description='Pipeline for feature engineering and data validation',
    schedule_interval='@hourly',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['creditpulse', 'feature_store'],
) as dag:

    start_pipeline = EmptyOperator(
        task_id='start_pipeline'
    )

    # Great Expectations Validation using the programmatic script
    validate_raw_data = BashOperator(
        task_id='validate_raw_data',
        bash_command='python /opt/airflow/great_expectations/validate.py',
    )

    # Run dbt to transform raw data into features and write to feature_store table
    run_dbt_models = BashOperator(
        task_id='run_dbt_models',
        bash_command='cd /opt/airflow/dbt_project && dbt run --profiles-dir ../dbt_profiles',
    )

    # Optional for Palier D: Check drift and retrain
    check_drift_and_retrain = BashOperator(
        task_id='check_drift_and_retrain',
        bash_command='echo "Drift monitoring (Evidently) goes here. Calls ml/monitor.py"',
    )

    end_pipeline = EmptyOperator(
        task_id='end_pipeline'
    )

    # Define DAG dependencies
    start_pipeline >> validate_raw_data >> run_dbt_models >> check_drift_and_retrain >> end_pipeline
