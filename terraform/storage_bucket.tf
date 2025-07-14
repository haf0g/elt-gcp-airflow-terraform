# the nmain bucket that will hold the CSV file containing 1 million records

resource "google_storage_bucket" "medical_global_bucket" {
  name                     = "etl-airflow-project-data-hafid"
  location                 = "US"
  force_destroy            = true
  public_access_prevention = "enforced"
  labels = {
    environment = "dev"
    project     = "elt-with-gcp-and-airflow"
    owner       = "hafid"
  }

  versioning {
    enabled = true
  }
}
