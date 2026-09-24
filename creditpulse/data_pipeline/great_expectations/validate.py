import os
import sys
import great_expectations as ge
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.types.base import DataContextConfig, DatasourceConfig
from great_expectations.data_context import BaseDataContext

def run_validation():
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    
    # Configure an in-memory DataContext
    project_config = DataContextConfig(
        datasources={
            "my_postgres_db": DatasourceConfig(
                class_name="Datasource",
                execution_engine={
                    "class_name": "SqlAlchemyExecutionEngine",
                    "connection_string": db_url,
                },
                data_connectors={
                    "default_inferred_data_connector_name": {
                        "class_name": "InferredAssetSqlDataConnector",
                        "name": "whole_table",
                    },
                },
            )
        },
        store_backend_defaults=ge.data_context.types.base.InMemoryStoreBackendDefaults(),
    )
    
    context = BaseDataContext(project_config=project_config)
    
    # Create the expectation suite
    suite_name = "financial_profiles_suite"
    suite = context.create_expectation_suite(suite_name, overwrite_existing=True)
    
    # Define batch request for the table
    batch_request = BatchRequest(
        datasource_name="my_postgres_db",
        data_connector_name="default_inferred_data_connector_name",
        data_asset_name="financial_profiles",
    )
    
    # Get a validator
    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name,
    )
    
    # Add expectations
    # 1. revenu_mensuel not null and >= 0
    validator.expect_column_values_to_not_be_null("revenu_mensuel")
    validator.expect_column_values_to_be_between("revenu_mensuel", min_value=0)
    
    # 2. age between 18 and 100
    validator.expect_column_values_to_not_be_null("age")
    validator.expect_column_values_to_be_between("age", min_value=18, max_value=100)
    
    # 3. dettes_actuelles >= 0
    validator.expect_column_values_to_not_be_null("dettes_actuelles")
    validator.expect_column_values_to_be_between("dettes_actuelles", min_value=0)
    
    # Save the suite
    validator.save_expectation_suite(discard_failed_expectations=False)
    
    # Run the checkpoint
    checkpoint_name = "financial_profiles_checkpoint"
    context.add_or_update_checkpoint(
        name=checkpoint_name,
        config_version=1,
        class_name="SimpleCheckpoint",
        validations=[
            {
                "batch_request": batch_request,
                "expectation_suite_name": suite_name,
            }
        ],
    )
    
    result = context.run_checkpoint(checkpoint_name=checkpoint_name)
    
    if not result["success"]:
        print("Data validation failed!")
        sys.exit(1)
        
    print("Data validation passed successfully.")

if __name__ == "__main__":
    run_validation()
