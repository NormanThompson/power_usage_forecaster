from forecast.modeling.data import load_demand, load_weather
from forecast.modeling.features import add_calendar_features, add_weather_features, DEFAULT_LAGS, add_lag_features
from forecast.modeling.cleaning import clean_demand
import pandas


def assemble_dataset(demand, weather, lags=DEFAULT_LAGS)-> pandas.DataFrame:
    """
    creates a dataset with all relevant information, using functions from the features module. Also removes
    bugs in the given demand data, and removes rows where demand isn't associated with a matching temperature
    :param demand: the demand dataset input
    :param weather: the weather dataset input
    :param lags: the lag for naive baseline comparisons & are factored into the prediction
    :return:  a dataframe with demand joined to weather data
    """
    demand = clean_demand(demand)
    demand = add_calendar_features(demand)
    weather = add_weather_features(weather)
    df = demand.join(weather)
    df = add_lag_features(df, lags)
    df = df.dropna(subset=["temp_c"])
    return df


def build_dataset(ba=None, location=None, lags=DEFAULT_LAGS)-> pandas.DataFrame:
    """
    Helper method to call assemble dataset, which does the work for creating the joint dataset
    :param ba: the balancing authority we are reading from
    :param location: the location we are gathering weather data from
    :param lags: the lag for naive baseline comparisons are factored into the prediction
    :return: a dataframe with demand joined to weather data
    """
    return assemble_dataset(load_demand(ba), load_weather(location), lags)

