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

def load_weather(location:str | None = None) -> pandas.DataFrame:
    """
    Loads weather data from weather_hourly table for a location
    :param location: the location we are pulling weather from
    :return: a dataframe with sorted, UTC time indexed data, and a column with temp_c for each index
    """
    location = location or get_settings().weather_location
    query = text(
        "select ts_utc, temp_c from weather_hourly where location = :location order by ts_utc asc"
    )
    df = pandas.read_sql(query, get_engine(), params = {"location": location}, parse_dates= ["ts_utc"] ).set_index("ts_utc")
    return df