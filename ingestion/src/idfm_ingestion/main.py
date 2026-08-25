from datetime import date
from pathlib import Path

import pandas as pd

from idfm_ingestion.config import S3_BUCKET
from idfm_ingestion.idfm import IDFMClient
from idfm_ingestion.s3 import upload_file


DATASET = "arrets"


def main():

    client = IDFMClient()

    print(
        f"Downloading IDFM dataset: {DATASET}"
    )

    records = client.get_dataset(
        dataset=DATASET,
        page_size=100,
    )

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError(
            "IDFM dataset is empty"
        )

    print(
        f"Downloaded {len(df)} records"
    )

    ingestion_date = date.today().isoformat()

    output_dir = Path("tmp")
    output_dir.mkdir(exist_ok=True)

    output_file = (
        output_dir /
        f"{DATASET}_{ingestion_date}.parquet"
    )

    df.to_parquet(
        output_file,
        index=False,
    )

    s3_key = (
        f"raw/idfm/"
        f"dataset={DATASET}/"
        f"ingestion_date={ingestion_date}/"
        f"data.parquet"
    )

    upload_file(
        file_path=str(output_file),
        bucket=S3_BUCKET,
        key=s3_key,
    )

    #check dag update
    print(
        "dag update check"
    )


if __name__ == "__main__":
    main()