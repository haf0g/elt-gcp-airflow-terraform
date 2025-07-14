"""
Author: [Hafid GARHOUM]
Date: [2025-07-10]
Optimized for Airflow 3.0.2 
check : https://airflow.apache.org/docs/apache-airflow/3.0.2/best-practices.html#top-level-python-code 
"""

from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

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
source_table = f'{project_id}.{dataset_id}.global_data'
countries = ['USA', 'India', 'Germany', 'Japan', 'France', 'Canada', 'Italy']

def check_gcs_file(**context):
    """Check if file exists in GCS"""
    from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
    
    sensor = GCSObjectExistenceSensor(
        task_id='check_file_exists_internal',
        bucket='etl-airflow-project-data-hafid',
        object='global_health_data.csv',
        timeout=300,
        poke_interval=30,
        mode='poke',
    )
    return sensor.poke(context)

def load_csv_to_bq(**context):
    """Load CSV from GCS to BigQuery"""
    from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
    
    operator = GCSToBigQueryOperator(
        task_id='load_csv_to_bq_internal',
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
    return operator.execute(context)

def create_country_table(country, **context):
    """Create country-specific table"""
    from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
    
    operator = BigQueryInsertJobOperator(
        task_id=f'create_table_{country.lower()}_internal',
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
    return operator.execute(context)

# DAG definition
with DAG(
    dag_id='load_and_transform_optimized',
    default_args=default_args,
    description='Load a CSV file from GCS to BigQuery and create country-specific tables',
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['bigquery', 'gcs', 'csv', 'optimized'],
) as dag:

    # Task 1: Check if the file exists in GCS
    check_file_task = PythonOperator(
        task_id='check_file_exists',
        python_callable=check_gcs_file,
    )

    # Task 2: Load CSV from GCS to BigQuery
    load_csv_task = PythonOperator(
        task_id='load_csv_to_bq',
        python_callable=load_csv_to_bq,
    )

    # Task 3: Create country-specific tables
    create_table_tasks = []
    for country in countries:
        create_table_task = PythonOperator(
            task_id=f'create_table_{country.lower()}',
            python_callable=create_country_table,
            op_kwargs={'country': country},
        )
        create_table_tasks.append(create_table_task)
        
        # Set upstream dependency
        create_table_task.set_upstream(load_csv_task)

    # Define task dependencies
    check_file_task >> load_csv_task