import pandas

# EIA occasionally reports impossible values (e.g. -58,286 and 11,000+ MWh on
# 2024-01-05 for AVA, whose normal range is roughly 1,000-2,500 MWh).
MIN_MWH = 0.0
MAX_MWH = 5000.0


def require_hourly_index(df: pandas.DataFrame) -> None:
    """Raise if the index is not a sorted, gap-free hourly DatetimeIndex."""
    if not isinstance(df.index, pandas.DatetimeIndex):
        raise ValueError("DataFrame must have a DatetimeIndex")
    steps = df.index.to_series().diff().dropna()
    if not (steps == pandas.Timedelta(hours=1)).all():
        raise ValueError("Index must be sorted, unique and strictly hourly (no gaps)")


def clean_demand(
    df: pandas.DataFrame, min_mwh: float = MIN_MWH, max_mwh: float = MAX_MWH
) -> pandas.DataFrame:
    """Replace bad demand values by time interpolation.

    Expects a column `mwh` and a sorted hourly DatetimeIndex (UTC). Returns a copy
    with two added columns:
      - `clean`:   demand with bad hours filled in by linear interpolation
      - `imputed`: True for every hour that was filled in (bad or missing)

    Bad = missing, below `min_mwh`, or above `max_mwh`. The raw `mwh` column is
    left untouched.
    """
    require_hourly_index(df)
    df = df.copy()
    bad = df["mwh"].isna() | (df["mwh"] < min_mwh) | (df["mwh"] > max_mwh)
    df["clean"] = (
        df["mwh"].mask(bad).interpolate(method="time", limit_direction="both")
    )
    df["imputed"] = bad
    return df
