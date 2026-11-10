import numpy
import pandas
import pytest

from forecast.modeling.cleaning import clean_demand
from forecast.modeling.evaluation import score_naive_baselines
from forecast.modeling.features import add_calendar_features, add_lag_features


def hourly_frame(values, start="2024-01-01 00:00"):
    idx = pandas.date_range(start, periods=len(values), freq="h", tz="UTC", name="ts_utc")
    return pandas.DataFrame({"mwh": values}, index=idx)


def test_clean_demand_replaces_and_flags_bad_values():
    # spike, negative and NaN in the middle of a smooth ramp
    df = hourly_frame([1000, 1100, 11000, -58000, numpy.nan, 1500, 1600])
    out = clean_demand(df)

    assert out["imputed"].tolist() == [False, False, True, True, True, False, False]
    # linear fill between 1100 (idx 1) and 1500 (idx 5): 1200, 1300, 1400
    assert out["clean"].tolist() == pytest.approx([1000, 1100, 1200, 1300, 1400, 1500, 1600])
    assert out["mwh"].iloc[2] == 11000  # raw column untouched


def test_clean_demand_does_not_modify_input():
    df = hourly_frame([1000, 99999, 1200])
    clean_demand(df)
    assert list(df.columns) == ["mwh"]


def test_clean_demand_rejects_gaps():
    df = hourly_frame([1000, 1100, 1200, 1300]).drop(index=pandas.Timestamp("2024-01-01 01:00", tz="UTC"))
    with pytest.raises(ValueError):
        clean_demand(df)


def test_calendar_features_use_local_time():
    # 2024-01-01 08:00 UTC is midnight Pacific (UTC-8) on a Monday
    df = hourly_frame([1000], start="2024-01-01 08:00")
    out = add_calendar_features(df)
    assert out["hour"].iloc[0] == 0
    assert out["day_of_week"].iloc[0] == 0
    assert not out["is_weekend"].iloc[0]


def test_lag_features_shift_by_hours_and_flag_missing_history():
    df = clean_demand(hourly_frame(list(range(1000, 1000 + 200))))
    out = add_lag_features(df, lags=(24,))
    assert out["lag_24"].iloc[30] == df["clean"].iloc[6]
    assert out["lag_24_imputed"].iloc[:24].all()  # no history yet


def test_naive_baseline_is_exact_for_a_perfectly_daily_series():
    day = [1000 + 10 * h for h in range(24)]
    df = clean_demand(hourly_frame(day * 14))  # 14 identical days
    scores = score_naive_baselines(df)
    assert scores[24].mae == pytest.approx(0)
    assert scores[168].mae == pytest.approx(0)


def test_baselines_scored_on_same_hours():
    df = clean_demand(hourly_frame([1000 + (h % 24) for h in range(400)]))
    scores = score_naive_baselines(df)
    assert scores[24].errors.index.equals(scores[168].errors.index)
