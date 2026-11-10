"""Exploratory summaries of demand (average daily shapes). Used for analysis and
plots, not by the forecasting service. Expects the output of
`add_calendar_features` applied to cleaned data."""

import pandas

SEASONS = {
    "winter": (12, 1, 2),
    "spring": (3, 4, 5),
    "summer": (6, 7, 8),
    "fall": (9, 10, 11),
}


def filter_months(df: pandas.DataFrame, months) -> pandas.DataFrame:
    """Rows whose local month is in `months`."""
    return df[df["month"].isin(list(months))]


def hourly_means(df: pandas.DataFrame) -> pandas.Series:
    """Average cleaned demand by local hour of day (0-23)."""
    return df.groupby("hour")["clean"].mean()


def weekday_weekend_means(df: pandas.DataFrame) -> pandas.DataFrame:
    """Average demand by local hour, with `weekday` and `weekend` columns."""
    table = df.groupby(["is_weekend", "hour"])["clean"].mean().unstack(0)
    return table.rename(columns={False: "weekday", True: "weekend"})


def seasonal_means(df: pandas.DataFrame) -> pandas.DataFrame:
    """Average demand by local hour, one column per season."""
    return pandas.concat(
        {name: hourly_means(filter_months(df, months)) for name, months in SEASONS.items()},
        axis=1,
    )
