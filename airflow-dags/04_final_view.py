"""
Author: [Hafid GARHOUM]
Date: [2025-07-10]
Optimized for Airflow 3.0.2 - Reduced import time
check : https://airflow.apache.org/docs/apache-airflow/3.0.2/best-practices.html#top-level-python-code 
"""

from datetime import datetime
from airflow import DAG
from airflow.providers.standard.operators.empty import EmptyOperator  # Updated for Airflow 3.0+


# Move heavy imports inside functions to reduce DAG parsing time
def get_gcs_sensor():
    from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
    return GCSObjectExistenceSensor

def get_gcs_to_bq_operator():
    from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
    return GCSToBigQueryOperator

def get_bq_operator():
    from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
    return BigQueryInsertJobOperator

# DAG default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define project, dataset, and table details
project_id = 'projetdata-461501'
dataset_id = 'dev_staging_dataset'
transform_dataset_id = 'dev_transformed_dataset'
reporting_dataset_id = 'dev_reporting_dataset'
source_table = f'{project_id}.{dataset_id}.global_data'  # Main table loaded from CSV
countries = ['USA', 'India', 'Germany', 'Japan', 'France', 'Canada', 'Italy']  # Country-specific tables to be created

# DAG definition
with DAG(
    dag_id='final_view',  # Updated DAG ID to match your requirement
    default_args=default_args,
    description='Load a CSV file from GCS to BigQuery and create country-specific tables',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['bigquery', 'gcs', 'csv'],
) as dag:

    # Task 1: Check if the file exists in GCS
    GCSObjectExistenceSensor = get_gcs_sensor()
    check_file_exists = GCSObjectExistenceSensor(
        task_id='check_file_exists',
        bucket='etl-airflow-project-data-hafid',
        object='global_health_data.csv',
        timeout=300,
        poke_interval=30,
        mode='poke',
    )

    # Task 2: Load CSV from GCS to BigQuery
    GCSToBigQueryOperator = get_gcs_to_bq_operator()
    load_csv_to_bigquery = GCSToBigQueryOperator(
        task_id='load_csv_to_bq',
        bucket='etl-airflow-project-data-hafid',
        source_objects=['global_health_data.csv'],
        destination_project_dataset_table=source_table,
        source_format='CSV',
        allow_jagged_rows=True,
        ignore_unknown_values=True,
        write_disposition='WRITE_TRUNCATE',
        skip_leading_rows=1,
        field_delimiter=',',
        autodetect=True,
    )

    # Tasks 3: Create country-specific tables and store them in a list
    BigQueryInsertJobOperator = get_bq_operator()
    create_table_tasks = []
    create_view_tasks = []
    
    for country in countries:
        # Task to create country-specific tables
        create_table_task = BigQueryInsertJobOperator(
            task_id=f'create_table_{country.lower()}',
            configuration={
                "query": {
                    "query": f"""
                        CREATE OR REPLACE TABLE `{project_id}.{transform_dataset_id}.{country.lower()}_table` AS
                        SELECT *
                        FROM `{source_table}`
                        WHERE country = '{country}'
                    """,
                    "useLegacySql": False,
                }
            },
        )

        # Task to create view for each country-specific table with selected columns and filter
        create_view_task = BigQueryInsertJobOperator(
            task_id=f'create_view_{country.lower()}_table',
            configuration={
                "query": {
                    "query": f"""
                        CREATE OR REPLACE VIEW `{project_id}.{reporting_dataset_id}.{country.lower()}_view` AS
                        SELECT 
                            `Year` AS `year`, 
                            `Disease Name` AS `disease_name`, 
                            `Disease Category` AS `disease_category`, 
                            `Prevalence Rate` AS `prevalence_rate`, 
                            `Incidence Rate` AS `incidence_rate`
                        FROM `{project_id}.{transform_dataset_id}.{country.lower()}_table`
                        WHERE `Availability of Vaccines Treatment` = False
                    """,
                    "useLegacySql": False,
                }
            },
        )

        # Set dependencies for table creation and view creation
        create_table_task.set_upstream(load_csv_to_bigquery)
        create_view_task.set_upstream(create_table_task)
        
        create_table_tasks.append(create_table_task)
        create_view_tasks.append(create_view_task)

    # Empty success task to run after all tables and views are created
    success_task = EmptyOperator(
        task_id='success_task',
    )

    # Define task dependencies
    check_file_exists >> load_csv_to_bigquery
    for create_table_task, create_view_task in zip(create_table_tasks, create_view_tasks):
        create_table_task >> create_view_task >> success_task