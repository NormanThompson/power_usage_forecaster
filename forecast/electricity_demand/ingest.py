"""Ingest EIA hourly demand into Postgres. Usage:
    python -m forecast.electricity_demand.ingest backfill --start 2023-01-01
    python -m forecast.electricity_demand.ingest update --days X"""

import argparse
from datetime import datetime, timedelta, timezone

from forecast.config import get_settings
from forecast.db.models import demand_hourly
from forecast.db.session import create_tables, upsert
from forecast.electricity_demand.eia_client import fetch_demand


def ingest(start: str, end: str | None = None) -> int:
    s = get_settings()
    create_tables()
    rows = fetch_demand(s.eia_api_key, s.ba_code, start, end)
    return upsert(demand_hourly, rows)


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("backfill")
    b.add_argument("--start", required=True, help="YYYY-MM-DD")
    u = sub.add_parser("update")
    u.add_argument("--days", type=int, default=7)
    args = p.parse_args()

    if args.cmd == "backfill":
        start = f"{args.start}T00"
    else:
        start = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime("%Y-%m-%dT%H")
    n = ingest(start)
    print(f"Upserted {n} rows for {get_settings().ba_code} from {start}")


if __name__ == "__main__":
    main()
