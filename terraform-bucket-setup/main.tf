provider "google" {
  project     = "projetdata-461501"
  credentials = file("../projetdata-461501-2196ced4898b.json")
  region      = "us-central1"
  
}

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
