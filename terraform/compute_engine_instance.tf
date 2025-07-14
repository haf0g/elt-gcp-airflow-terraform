resource "google_compute_instance" "airflow_instance" {
  name         = "airflow-instance"
  machine_type = "e2-medium"  # Adjust as needed
  zone         = "us-central1-a"  # Adjust to your zone

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-12"  # Adjust the image
      size  = 10
    }
  }

  network_interface {
    network = "default"
    access_config {
      # Assign external IP if needed
    }
  }

  # Attach the service account
  service_account {
    email  = "composer-custom-sa@projetdata-461501.iam.gserviceaccount.com"
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]  # Adjust based on permissions you need
  }

  labels = {
    environment = "dev"
    project     = "elt-with-gcp-and-airflow"
    owner       = "hafid"
  }
}
