from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Settings configuration read from .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    eia_api_key: str
    database_url: str = "postgresql+psycopg://forecast:forecast_local@localhost:5432/forecast"

    ba_code: str = "AVA"  # EIA balancing authority code (Avista)
    weather_lat: float = 47.6588  # Spokane
    weather_lon: float = -117.4260


def get_settings() -> Settings:
    return Settings()
