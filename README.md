
#  ELT Data Pipeline with GCP, Airflow, and Terraform

This project demonstrates how to build a **scalable ELT** (Extract–Load–Transform) data pipeline in **Google Cloud Platform (GCP)**, powered by **Apache Airflow** and fully provisioned via **Terraform**. It processes a global health dataset of over **1 million records**, extracts it to **GCS**, loads it into **BigQuery**, and transforms it into secure, country-specific datasets for reporting.

## ✨ Features

- **Terraform Automation**:
  - GCS bucket
  - BigQuery datasets: `dev_staging_dataset`, `dev_transformed_dataset`, `dev_reporting_dataset`
  - Compute Engine VM for Airflow
- **Airflow Orchestration**:
  - Checks for file existence in GCS
  - Loads raw CSV into BigQuery staging table
  - Applies transformations:
    - Build cleaned tables in `dev_transformed_dataset`
    - Expose country-specific reporting views
- **Secure Data Segmentation**:
  - Each country's users can access relevant data with a global view that assembles all countries for more high hierarchique decison takers
  - Analysis on diseases without available treatments
- **Consumption Layer**:
  - Build Looker dashboards on reporting views
  - Send scheduled Gmail reports to stakeholders

## 🛠 Architecture & Workflow

>![Project Diagram](/img/project-Diagram.png)
>

1. **Provisioning**  
   Terraform spins up:
   - GCS bucket for raw CSV
   - BigQuery datasets
   - Airflow VM on Compute Engine

2. **ELT Pipeline**  
   - **Extract**: Airflow detects file in GCS  
   - **Load**: Moves the data to BigQuery staging  
   - **Transform**:  
     - Normalize into transformed_dataset  
     - Generate country-specific reporting views for GCP optimized performance in querying

3. **Secure Delivery**  
   - Sensitive data stays partitioned
   - Reporting layers filtered by country and disease treatment availability

4. **Dashboard & Alerts**

> <img width="1350" height="758" alt="Capture d'écran 2025-07-13 002131" src="https://github.com/user-attachments/assets/7e0cadfd-59cf-490b-b7ed-c043ed3c16ee" />
>

   - Looker retrieves reporting tables  
   - Scheduled Gmail alerts notify stakeholders

## 📚 Project Requirements & Setup

1. GCP project with billing, Compute, Storage, and BigQuery APIs enabled  
2. Service account with roles: 
   - Compute Admin
   - Storage Admin
   - BigQuery Admin  
 
3. Terraform (v1.0+), `gcloud` CLI authenticated  
4. Python environment with Airflow and Google provider packages

### Quickstart

```bash
# Clone and provision the bucket:
git clone https://github.com/haf0g/elt-gcp-airflow-terraform.git
cd terraform-bucket-setup

# Initialize remote state backend (GCS):
terraform init
terraform apply

# Now we will provision the full infra as it depnds on the bucket existence
cd ..
cd terraform

terraform init
terraform apply

# Deploy Airflow Dags : Copy dags from local to VM instance in GCP DAGs:
scp airflow-dags/* VM-username@VM-external-IP:/home/airflow/dags/
```

## 🏆 Output

- BigQuery datasets with:
  - `staging` (raw)
  - `transform` (cleaned and country based tables creation)
  - `reporting` (country views)
- Secure data segmentation ensuring confidentiality
- Looker visualizations and scheduled reports live via Gmail


