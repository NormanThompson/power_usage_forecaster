import argparse
from datetime import datetime, timedelta, timezone

from forecast.config import get_settings
from forecast.db.models import weather_hourly
from forecast.db.session import create_tables, upsert
from forecast.weather.open_meteo_client import fetch_archive

def ingest(start: str, end: str | None = None) -> int:
    s = get_settings()
    create_tables()
    rows = fetch_archive(s.weather_lat, s.weather_lon, s.weather_location, start, end)
    return upsert(weather_hourly, rows)

def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backfill")
    b.add_argument("--start", required=True, help="YYYY-MM-DD")
    u = sub.add_parser("update")
    u.add_argument("--days", type=int, default=7)
    args = p.parse_args()

    if args.cmd == "backfill":
        start = args.start
    else:
        start = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%d")
    n = ingest(start)
    print(f"Upserted {n} rows for {get_settings().weather_location} from {start}")


if __name__ == "__main__":
    main()
