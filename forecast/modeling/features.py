import pandas

from forecast.modeling.cleaning import require_hourly_index

LOCAL_TZ = "America/Los_Angeles"  # Pacific time (PST/PDT), observes daylight saving
DEFAULT_LAGS = (24, 168)  # same hour yesterday, same hour last week (in hours)


def add_calendar_features(df: pandas.DataFrame, tz: str = LOCAL_TZ) -> pandas.DataFrame:
    """Add local-time calendar columns without changing the (UTC) index.

    Adds `hour` (0-23), `day_of_week` (0=Monday ... 6=Sunday), `month` (1-12)
    and `is_weekend`, all in local time.
    """
    df = df.copy()
    local = df.index.tz_convert(tz)
    df["hour"] = local.hour
    df["day_of_week"] = local.day_of_week
    df["month"] = local.month
    df["is_weekend"] = df["day_of_week"] >= 5
    return df


def add_lag_features(df: pandas.DataFrame, lags=DEFAULT_LAGS) -> pandas.DataFrame:
    """Add `lag_<n>` (demand n hours earlier) and `lag_<n>_imputed` columns.

    Needs `clean` and `imputed` columns and a gap-free hourly index, so that
    shifting by n rows really means shifting by n hours. For a day-ahead forecast
    use lags of at least 24 hours: shorter lags would not be known in advance.
    """
    require_hourly_index(df)
    df = df.copy()
    for lag in lags:
        df[f"lag_{lag}"] = df["clean"].shift(lag)
        # fill_value=True: rows with no history can't be scored
        df[f"lag_{lag}_imputed"] = df["imputed"].shift(lag, fill_value=True)
    return df
