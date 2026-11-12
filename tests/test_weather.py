import numpy
import pandas
import pytest

from forecast.modeling.features import add_weather_features

def test_degrees_split_at_balance_point():
    df = pandas.DataFrame({"temp_c": [0.0, 6.0, 14.0, 25.0, 30.0, 3.4, 18.8, numpy.nan]})
    out = add_weather_features(df, balance_point=14)
    assert out["usage_degrees_heating"].iloc[:-1].to_list() == pytest.approx([14.0, 8.0, 0.0, 0.0, 0.0, 10.6, 0.0])
    assert out["usage_degrees_cooling"].iloc[:-1].to_list() == pytest.approx([0.0, 0.0, 0.0, 11.0, 16.0, 0.0, 4.8])

    assert out["usage_degrees_cooling"].isna().to_list() == [False, False, False, False, False, False, False, True ]
    assert out["usage_degrees_heating"].isna().to_list() == [False, False, False, False, False, False, False, True ]