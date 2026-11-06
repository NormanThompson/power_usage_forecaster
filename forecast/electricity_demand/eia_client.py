from datetime import datetime, timezone
import requests
EIA_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
PAGE_SIZE = 5000  # max allowable per request

def fetch_demand(api_key: str, ba: str, start: str, end: str | None = None) -> list[dict]:
    """This fetches hourly demand for one balancing authority (currently AVA is used by default).
    `start`/`end` are EIA period strings like "2023-01-01T00" (UTC). Pages through
    all results and returns rows shaped for the demand_hourly table."""
    rows: list[dict] = []
    offset = 0
    while True:
        params = {
            "api_key": api_key,
            "frequency": "hourly",
            "data[0]": "value",
            "facets[respondent][]": ba,
            "facets[type][]": "D",
            "start": start,
            "sort[0][column]": "period",
            "sort[0][direction]": "asc",
            "offset": offset,
            "length": PAGE_SIZE,
        }
        if end:
            params["end"] = end
        resp = requests.get(EIA_URL, params=params, timeout=60)
        resp.raise_for_status()
        body = resp.json()["response"]
        data = body["data"]
        for r in data:
            value = r.get("value")
            rows.append(
                {
                    "ba": r["respondent"],
                    "ts_utc": datetime.strptime(r["period"], "%Y-%m-%dT%H").replace(
                        tzinfo=timezone.utc
                    ),
                    "mwh": float(value) if value is not None else None,
                }
            )
        if len(data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows
