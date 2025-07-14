terraform {
  backend "gcs" {
    bucket      = "etl-airflow-project-data-hafid"
    prefix      = "terraform/state"
    credentials = "../projetdata-461501-2196ced4898b.json"
    }
}