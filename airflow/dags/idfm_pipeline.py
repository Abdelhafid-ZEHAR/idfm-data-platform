from datetime import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator


with DAG(
    dag_id="idfm_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["idfm", "ingestion"],
) as dag:

    ingest_idfm = KubernetesPodOperator(
        task_id="807225301812029",

        name="idfm-ingestion",
        namespace="default",

        image="idfm-ingestion:latest",
        image_pull_policy="Never",

        cmds=["python", "-m", "idfm_ingestion.main"],

        env_vars={
            "S3_ENDPOINT": "http://minio:9000",
            "S3_ACCESS_KEY": "minioadmin",
            "S3_SECRET_KEY": "minioadmin",
            "S3_BUCKET": "idfm-data",
        },

        get_logs=True,

        is_delete_operator_pod=True,
    )

    run_databricks_job = DatabricksRunNowOperator(
        task_id="run_databricks_job",

        databricks_conn_id="databricks_default",

        job_id=YOUR_JOB_ID,
    )

    ingest_idfm >> run_databricks_job