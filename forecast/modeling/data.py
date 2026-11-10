import pandas
from sqlalchemy import text

from forecast.config import get_settings
from forecast.db.session import get_engine


def load_demand(ba: str | None = None) -> pandas.DataFrame:
    """Load raw hourly demand for one balancing authority.

    Returns a DataFrame with a sorted, UTC-aware DatetimeIndex (`ts_utc`) and a
    single column `mwh` exactly as stored in the database (no cleaning).
    """
    ba = ba or get_settings().ba_code
    query = text(
        "select ts_utc, mwh from demand_hourly where ba = :ba order by ts_utc asc"
    )
    df = pandas.read_sql(query, get_engine(), params={"ba": ba}, parse_dates=["ts_utc"])
    return df.set_index("ts_utc")
