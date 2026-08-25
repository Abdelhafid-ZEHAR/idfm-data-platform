import requests


IDFM_API_URL = "https://data.iledefrance-mobilites.fr/api/explore/v2.1"


class IDFMClient:

    def __init__(self, base_url: str = IDFM_API_URL):
        self.base_url = base_url.rstrip("/")

    def get_dataset_page(
        self,
        dataset: str,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:

        url = (
            f"{self.base_url}/catalog/datasets/"
            f"{dataset}/records"
        )

        params = {
            "limit": limit,
            "offset": offset,
        }

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            print(f"HTTP error: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Response: {response.text[:1000]}")
            raise

        return response.json()

    def get_dataset(
    self,
    dataset: str,
    page_size: int = 100,
    ):

        if not 1 <= page_size <= 100:
            raise ValueError(
                "page_size must be between 1 and 100"
            )

        offset = 0
        while True:
            if offset >= 10000:
                break
            data = self.get_dataset_page(
                dataset=dataset,
                limit=page_size,
                offset=offset,
            )

            records = data["results"]

            if not records:
                break

            yield from records

            offset += len(records)

            if offset >= data["total_count"]:
                breaks