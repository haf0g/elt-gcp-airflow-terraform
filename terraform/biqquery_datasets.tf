# Creating the datasets for the 3 different layers that we need for data processing

resource "google_bigquery_dataset" "datasets" {
  for_each = { for dataset in var.datasets : dataset.id => dataset }

  dataset_id    = "${var.environment}_${each.value.id}"  # This adds "dev_" prefix
  friendly_name = each.value.friendly_name
  description   = each.value.description
  location      = each.value.location

  # Auto-delete old tables after 90 days (optional)
  default_table_expiration_ms = 7776000000

  # Better labels
  labels = {
    environment = var.environment
    layer       = each.value.id
    managed_by  = "terraform"
  }
}