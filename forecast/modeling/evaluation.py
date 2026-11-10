from typing import NamedTuple

import pandas

from forecast.modeling.features import DEFAULT_LAGS, add_lag_features


class BaselineScore(NamedTuple):
    lag: int  # hours back that the naive forecast copies from
    errors: pandas.Series  # absolute error per scored hour (MWh)
    mae: float  # mean absolute error (MWh)
    mape: float  # mean absolute percentage error (%)


def valid_mask(df: pandas.DataFrame, lag: int) -> pandas.Series:
    """Hours that can be fairly scored for the given lag.

    An hour is scorable when its lagged value exists and neither the actual
    value nor the lagged (predicted) value was imputed.
    """
    return (
        df[f"lag_{lag}"].notna()
        & ~df["imputed"]
        & ~df[f"lag_{lag}_imputed"]
    )


def score_naive_baselines(
    df: pandas.DataFrame, lags=DEFAULT_LAGS
) -> dict[int, BaselineScore]:
    """Score "same hour `lag` hours ago" forecasts against actual demand.

    Every baseline is scored on the same set of hours (valid for all lags), so
    the results are directly comparable. Expects `clean` and `imputed` columns.
    """
    d = add_lag_features(df, lags)
    valid = pandas.concat([valid_mask(d, lag) for lag in lags], axis=1).all(axis=1)
    actual = d.loc[valid, "clean"]

    scores = {}
    for lag in lags:
        errors = (actual - d.loc[valid, f"lag_{lag}"]).abs()
        mape = (errors / actual.where(actual > 0)).mean() * 100
        scores[lag] = BaselineScore(lag, errors, errors.mean(), mape)
    return scores
