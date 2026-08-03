# Great Expectations (Palier B.2)

À IMPLÉMENTER : suite de validation avec des expectations comme :
- expect_column_values_to_not_be_null (revenu_mensuel, age)
- expect_column_values_to_be_between (age, 18, 100)
- expect_column_values_to_be_between (revenu_mensuel, 0, None)

Initialiser avec `great_expectations init` puis créer un checkpoint
appelé par la tâche `validate_raw_data` du DAG Airflow.
