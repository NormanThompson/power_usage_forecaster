from datetime import datetime, timezone, timedelta
import requests

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

def parse_hourly(response_json:dict, location:str) -> list[dict]:
    times = response_json["hourly"]["time"]
    temps = response_json["hourly"]["temperature_2m"]
    rows = []
    for t, temp in zip(times, temps):
        ts_utc = datetime.strptime(t, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
        rows.append({"location": location, "ts_utc": ts_utc, "temp_c": temp})
    return rows

def fetch_archive(lat:float, lon:float,location:str, start_date:str, end_date:str|None = None)->list[dict]:
    if end_date is None:
        end_date = str(datetime.now(timezone.utc).date() -timedelta(days = 1))
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m",
        "timezone": "UTC"
    }
    resp = requests.get(ARCHIVE_URL, params = params, timeout = 60)
    resp.raise_for_status()
    return parse_hourly(resp.json(), location)
