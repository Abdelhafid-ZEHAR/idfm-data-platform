import pandas as pd


def records_to_dataframe(records):

    df = pd.DataFrame(records)

    if df.empty:
        raise ValueError("IDFM API returned no records")

    return df