variable "gcp_project_id" {
  description = "The ID of the GCP project"
  type        = string
}

variable "gcp_region" {
  description = "The GCP region to deploy resources in"
  type        = string
}

variable "environment" {
  description = "Environment name (e.g., dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "datasets" {
  default = [
    {
      id            = "staging_dataset"
      friendly_name = "Staging Dataset"
      description   = "Dataset for staging raw data"
      location      = "US"
    },
    {
      id            = "transformed_dataset"
      friendly_name = "Transformed Dataset"
      description   = "Dataset for storing transformed data"
      location      = "US"
    },
    {
      id            = "reporting_dataset"
      friendly_name = "Reporting Dataset"
      description   = "Dataset for final reporting views"
      location      = "US"
    }
  ]
}