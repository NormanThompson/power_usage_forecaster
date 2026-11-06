from sqlalchemy import Column, DateTime, Float, MetaData, String, Table

metadata = MetaData()

# Hourly electricity demand per balancing authority (MWh, EIA type "D").
demand_hourly = Table(
    "demand_hourly",
    metadata,
    Column("ba", String(10), primary_key=True),
    Column("ts_utc", DateTime(timezone=True), primary_key=True),
    Column("mwh", Float, nullable=True),
)

# Hourly temperature per weather location.
weather_hourly = Table(
    "weather_hourly",
    metadata,
    Column("location", String(50), primary_key=True),
    Column("ts_utc", DateTime(timezone=True), primary_key=True),
    Column("temp_c", Float, nullable=True),
)
