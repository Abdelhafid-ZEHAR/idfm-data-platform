# 🚆 IDFM Data Platform

An end-to-end data engineering platform that ingests Île-de-France Mobilités (IDFM) data, stores it in an S3-compatible data lake, and processes it through a **Bronze → Silver → Gold** architecture using **Apache Airflow, Kubernetes, MinIO, and Databricks**.

The platform is designed as a local/cloud hybrid data engineering project, with Kubernetes used for orchestration and MinIO providing an S3-compatible object store.

---

## 🏗️ Architecture

```text
                         ┌──────────────────┐
                         │    IDFM API      │
                         │  Public Dataset  │
                         └────────┬─────────┘
                                  │
                                  │ HTTP
                                  ▼
                         ┌──────────────────┐
                         │     Airflow      │
                         │   Kubernetes     │
                         │                  │
                         │   Ingestion DAG  │
                         └────────┬─────────┘
                                  │
                                  │ write
                                  ▼
                         ┌──────────────────┐
                         │      MinIO       │
                         │   S3 Data Lake   │
                         │                  │
                         │      RAW         │
                         └────────┬─────────┘
                                  │
                                  │ trigger
                                  ▼
                         ┌──────────────────┐
                         │    Databricks    │
                         │                  │
                         │     Bronze       │
                         │        ↓         │
                         │     Silver       │
                         │        ↓         │
                         │      Gold        │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      MinIO       │
                         │   S3 Data Lake   │
                         │                  │
                         │ Bronze/Silver/   │
                         │      Gold        │
                         └──────────────────┘
```

---

# 🎯 Project Goals

The project demonstrates a complete modern data engineering workflow:

* Consume data from a public API
* Orchestrate ingestion with Apache Airflow
* Run Airflow on Kubernetes
* Store raw data in an S3-compatible data lake
* Use MinIO as local S3 infrastructure
* Trigger Databricks Jobs from Airflow
* Transform data using Spark
* Implement a Medallion architecture
* Produce clean analytical datasets
* Separate orchestration from data processing
* Use Kubernetes secrets for credentials
* Use Git-sync to deploy DAGs automatically

---

# 🧰 Technology Stack

| Component               | Technology                            |
| ----------------------- | ------------------------------------- |
| Data source             | Île-de-France Mobilités API           |
| Orchestration           | Apache Airflow 3.2.2                  |
| Container orchestration | Kubernetes                            |
| Local Kubernetes        | kind                                  |
| Object storage          | MinIO                                 |
| Storage protocol        | S3                                    |
| Data processing         | Databricks / Apache Spark             |
| Data format             | Parquet                               |
| Programming             | Python / PySpark                      |
| DAG deployment          | Git-sync                              |
| Package management      | Helm                                  |
| Cloud tunnel            | Cloudflare Tunnel                     |
| Authentication          | Kubernetes Secrets / Databricks Token |

---

# 📁 Project Structure

```text
idfm-data-platform/
│
├── airflow/
│   └── dags/
│       ├── idfm_pipeline.py
│       └── databricks_pipeline.py
│
├── databricks/
│   ├── bronze/
│   ├── silver/
│   └── gold/
│
├── ingestion/
│   └── idfm_ingestion/
│       └── main.py
│
├── infrastructure/
│   ├── airflow/
│   │   └── values.yaml
│   │
│   ├── kubernetes/
│   │   ├── minio/
│   │   └── ...
│
└── README.md
```

---

# 🌊 Data Lake Architecture

The data lake follows a Medallion architecture.

```text
MinIO
│
├── raw/
│   └── idfm/
│       └── dataset=arrets/
│
├── bronze/
│   └── idfm/
│
├── silver/
│   └── idfm/
│
└── gold/
    └── idfm/
```

## Raw

Raw data is stored as close as possible to the original source.

Example:

```text
s3://idfm-data/raw/idfm/dataset=arrets/
```

The raw layer is intended to preserve the original data and provide a reproducible ingestion point.

---

# 🥉 Bronze Layer

The Bronze layer contains data that has been ingested into the processing environment with minimal transformation.

Typical operations include:

* Reading raw Parquet files
* Schema normalization
* Basic type handling
* Adding ingestion metadata

Example metadata:

```text
_processed_at
```

The Bronze layer acts as the first structured representation of the raw data.

---

# 🥈 Silver Layer

The Silver layer contains cleaned and standardized datasets.

For the IDFM `arrets` dataset, the transformation includes:

```text
arrid              → arrid
arrversion         → arrversion
arrcreated         → created_at
arrchanged         → changed_at
arrname            → name
arrtype            → type
arrtown            → town
arrpostalregion    → postal_region
arraccessibility   → accessibility
arraudiblesignals  → audible_signals
arrvisualsigns     → visual_signs
arrfarezone        → fare_zone
arrxepsg2154       → x_epsg2154
arryepsg2154       → y_epsg2154
arrgeopoint.lat    → latitude
arrgeopoint.lon    → longitude
zdaid              → zda_id
```

The resulting schema is approximately:

```text
root
├── arrid: string
├── arrversion: string
├── created_at: timestamp
├── changed_at: timestamp
├── name: string
├── type: string
├── town: string
├── postal_region: string
├── accessibility: string
├── audible_signals: string
├── visual_signs: string
├── fare_zone: string
├── x_epsg2154: long
├── y_epsg2154: long
├── latitude: double
├── longitude: double
├── zda_id: string
└── _silver_processed_at: timestamp
```

---

# 🥇 Gold Layer

The Gold layer contains business-oriented datasets designed for analytics and downstream applications.

The objective is to transform the cleaned Silver data into datasets that directly answer business questions.

Examples could include:

* Number of stops by municipality
* Stops by transport type
* Accessibility statistics
* Geographic distribution of stops
* Stops by fare zone
* IDFM network statistics

---

# 🔄 End-to-End Pipeline

The complete workflow is:

```text
1. IDFM API
      │
      ▼
2. Airflow ingestion DAG
      │
      ▼
3. Raw data
      │
      ▼
4. MinIO
      │
      ▼
5. Airflow triggers Databricks Job
      │
      ▼
6. Databricks reads Raw
      │
      ▼
7. Bronze transformation
      │
      ▼
8. Silver transformation
      │
      ▼
9. Gold transformation
      │
      ▼
10. Write processed datasets to MinIO
```

---

# ☁️ Airflow

Airflow runs inside Kubernetes.

The deployment uses the official Apache Airflow Helm chart.

The DAGs are automatically synchronized from GitHub using `git-sync`.

```text
GitHub
   │
   │ git-sync
   ▼
Airflow DAG Processor
   │
   ▼
Airflow Scheduler
   │
   ▼
Airflow Worker
```

## DAG responsibilities

### Ingestion task

The ingestion task:

1. Calls the IDFM API
2. Downloads the data
3. Creates the required dataset
4. Writes the raw data to MinIO

### Databricks task

The Databricks task:

1. Connects to Databricks
2. Triggers the Databricks Job
3. Passes control to Databricks for processing
4. Waits for the Databricks Job to complete
5. Reports success/failure to Airflow

---

# 🔐 Secrets

Credentials are not stored directly in the repository.

Kubernetes Secrets are used for:

```text
airflow-api-secret-key
databricks-credentials
airflow-metadata
```

The Databricks Airflow connection is exposed through:

```text
AIRFLOW_CONN_DATABRICKS_DEFAULT
```

The connection is loaded from the Kubernetes Secret:

```text
databricks-credentials
```

---

# 🧑‍💻 Local Setup

## Prerequisites

Install:

* Docker
* kubectl
* kind
* Helm
* Git

You also need:

* A Databricks account
* A Databricks workspace
* A Databricks Job
* A Databricks access token with the required Jobs permissions

---

# ☸️ Create the Kubernetes Cluster

Example:

```bash
kind create cluster --name idfm-platform
```

Verify:

```bash
kubectl get nodes
```

---

# 🚀 Deploy MinIO

Deploy MinIO inside the Kubernetes cluster.

Verify:

```bash
kubectl get pods -A
```

The MinIO pod should be running.

Verify the service:

```bash
kubectl get svc -A
```

The S3 API is exposed internally through the Kubernetes service.

Example endpoint:

```text
http://minio:9000
```

---

# 🚀 Deploy Airflow

Add the Airflow Helm repository:

```bash
helm repo add apache-airflow https://airflow.apache.org
helm repo update
```

Install/upgrade Airflow:

```bash
helm upgrade --install airflow apache-airflow/airflow \
  -n airflow \
  --create-namespace \
  -f infrastructure/airflow/values.yaml
```

Check:

```bash
kubectl get pods -n airflow
```

Expected components include:

```text
airflow-api-server
airflow-dag-processor
airflow-scheduler
airflow-worker
airflow-triggerer
airflow-postgresql
airflow-redis
```

---

# 🔄 Git-Sync

Airflow DAGs are automatically synchronized from GitHub.

Configuration:

```yaml
dags:
  gitSync:
    enabled: true
    repo: https://github.com/Abdelhafid-ZEHAR/idfm-data-platform.git
    branch: main
    ref: main
    depth: 1
    subPath: airflow/dags
    period: 5s
```

After pushing a DAG:

```bash
git add .
git commit -m "Add DAG"
git push
```

Git-sync automatically updates the DAGs inside Airflow.

---

# 🔗 Databricks Connection

Airflow uses the connection:

```text
databricks_default
```

The connection is provided through a Kubernetes Secret.

Verify it:

```bash
kubectl exec -n airflow deployment/airflow-scheduler \
  -c scheduler -- \
  airflow connections get databricks_default
```

The Databricks token must have permission to execute Jobs.

---

# ▶️ Running the Pipeline

Once Airflow and MinIO are running:

1. Open the Airflow UI.
2. Enable the IDFM ingestion DAG.
3. Trigger the DAG.
4. Verify that raw data appears in MinIO.
5. Trigger the Databricks processing DAG.
6. Airflow calls the Databricks Jobs API.
7. Databricks executes the Bronze → Silver → Gold transformations.
8. Processed Parquet datasets are written back to MinIO.

---

# 🔍 Useful Kubernetes Commands

Check Airflow pods:

```bash
kubectl get pods -n airflow
```

Check DAG processor logs:

```bash
kubectl logs -n airflow \
  deployment/airflow-dag-processor \
  -c dag-processor
```

Check worker logs:

```bash
kubectl logs -n airflow \
  airflow-worker-0 \
  -c worker
```

Check Git-sync:

```bash
kubectl logs -n airflow \
  deployment/airflow-dag-processor \
  -c git-sync
```

Check Helm:

```bash
helm status airflow -n airflow
```

Check Helm values:

```bash
helm get values airflow -n airflow
```

---

# 🧪 Troubleshooting

## DAG does not appear

Check Git-sync:

```bash
kubectl logs -n airflow \
  deployment/airflow-dag-processor \
  -c git-sync
```

Check that the repository contains:

```text
airflow/dags/
```

---

## Airflow secret-key error

All Airflow components must use the same:

```text
AIRFLOW__API__SECRET_KEY
```

The Helm configuration uses:

```yaml
apiSecretKeySecretName: airflow-api-secret-key
```

After changing the secret, restart the relevant Airflow components.

---

## Databricks 403 error

If Databricks returns:

```text
Provided access token does not have required scopes: jobs
```

the Databricks token does not have the permissions required to execute Jobs.

Create/use a token with the appropriate Jobs permissions and update:

```text
databricks-credentials
```

---

## KubernetesPodOperator 403

If Airflow returns an error such as:

```text
pods is forbidden
```

or:

```text
events is forbidden
```

check the Airflow worker's Kubernetes RBAC configuration.

---

# 🌐 Cloudflare Tunnel

A Cloudflare Tunnel can be used to expose services running inside the local Kubernetes cluster without directly exposing the cluster to the Internet.

Typical architecture:

```text
Internet
   │
   ▼
Cloudflare
   │
   │ Tunnel
   ▼
Local machine
   │
   ▼
Kubernetes
   │
   ├── Airflow
   └── MinIO
```

This is particularly useful when Databricks needs to access a service running locally.

---

# 📊 Current Data Flow

```text
              IDFM
               │
               │ API
               ▼
        ┌───────────────┐
        │    Airflow    │
        │  Kubernetes   │
        └───────┬───────┘
                │
                │ ingestion
                ▼
        ┌───────────────┐
        │     MinIO     │
        │               │
        │     RAW       │
        └───────┬───────┘
                │
                │ trigger
                ▼
        ┌───────────────┐
        │   Databricks  │
        │               │
        │    Bronze     │
        │       ↓       │
        │    Silver     │
        │       ↓       │
        │     Gold      │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │     MinIO     │
        │               │
        │ Bronze/Silver │
        │     /Gold     │
        └───────────────┘
```

---

# 🎓 What This Project Demonstrates

This project demonstrates practical experience with:

### Data Engineering

* ETL / ELT
* Data ingestion
* Data lakes
* Medallion architecture
* Parquet
* Data transformation
* Data quality
* Incremental processing

### Distributed Processing

* Apache Spark
* Databricks
* PySpark
* Distributed data processing

### Orchestration

* Apache Airflow
* DAG design
* Task dependencies
* External job orchestration

### Cloud / Infrastructure

* Kubernetes
* Helm
* Docker
* S3
* MinIO
* Cloudflare Tunnel

### DevOps

* Git
* Git-sync
* Kubernetes Secrets
* Containerized applications
* Infrastructure configuration

---

# 🚀 Future Improvements

Potential next steps:

* Add automated data-quality checks
* Add incremental ingestion
* Add partitioning strategies
* Add schema evolution
* Add Delta Lake
* Add monitoring and alerting
* Add Airflow retries and SLAs
* Add CI/CD
* Add automated Databricks deployment
* Add data lineage
* Add Great Expectations or another data-quality framework
* Add analytical dashboards
* Add automated end-to-end tests

---

# 👨‍💻 Author

**Abdelhafid ZEHAR**

Data Engineer

This project is built as a hands-on demonstration of a modern end-to-end data engineering architecture using Kubernetes, Airflow, MinIO, Spark, and Databricks.
