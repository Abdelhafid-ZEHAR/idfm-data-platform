import boto3

from idfm_ingestion.config import (
    S3_ACCESS_KEY,
    S3_ENDPOINT,
    S3_SECRET_KEY,
)


def get_s3_client():

    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name="us-east-1",
    )


def upload_file(
    file_path: str,
    bucket: str,
    key: str,
):

    s3 = get_s3_client()

    s3.upload_file(
        file_path,
        bucket,
        key,
    )

    print(
        f"Uploaded: s3://{bucket}/{key}"
    )