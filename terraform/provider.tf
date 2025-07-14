# State the cloud provider you will be working with
provider "google" {
  project     = var.gcp_project_id
  region      = var.gcp_region
  credentials = "../projetdata-461501-2196ced4898b.json"
}