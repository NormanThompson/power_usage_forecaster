import pandas
import pytest
from forecast.modeling.dataset import assemble_dataset
from forecast.modeling.evaluation import score_naive_baselines

def hourly_index(n, start="2024-01-01 00:00:00"):
    return pandas.date_range(start, periods = n, freq = "h", tz = "UTC", name = "ts_utc")

def make_data(n = 500):
    idx = hourly_index(n)
    demand = pandas.DataFrame({"mwh":[1000 + (h % 24) for h in range(n)]}, index = idx)
    weather = pandas.DataFrame({"temp_c": [10.0] * n}, index=idx)
    return demand, weather

def test_has_expected_columns():
    demand, weather = make_data()
    df = assemble_dataset(demand, weather)
    for col in ["clean", "imputed", "hour",
                "temp_c", "usage_degrees_heating",
                "usage_degrees_cooling", "lag_24", "lag_168"]:
        assert col in df.columns


def test_baselines_can_score_a_dataset_with_dropped_rows():
    demand, weather = make_data()
    weather = weather.drop(index=weather.index[250])  # leaves a gap in the dataset
    df = assemble_dataset(demand, weather)
    scores = score_naive_baselines(df)  # would raise ValueError if it recomputed lags
    assert scores[24].mae == pytest.approx(0)


def test_rows_without_temperatures_are_dropped():
    demand, weather = make_data()
    weather = weather.drop(index = weather.index[50])
    df = assemble_dataset(demand, weather)
    assert len(df) == len(demand) - 1
    assert demand.index[50] not in df.index
