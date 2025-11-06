import pandera as pa
from pandera.pandas import DataFrameModel
from pandera.typing import DataFrame, Series


class WeatherStation(DataFrameModel):
    station_code: Series[str] = pa.Field(coerce=True)
    station_name: Series[str] = pa.Field(nullable=True)
    region: Series[str] = pa.Field(nullable=True)
    state: Series[str] = pa.Field(nullable=True)
    latitude: Series[float] = pa.Field(nullable=True)
    longitude: Series[float] = pa.Field(nullable=True)
    altitude: Series[float] = pa.Field(nullable=True)
    start_date: Series[str] = pa.Field(nullable=True)
    source_file: Series[str] = pa.Field(nullable=True)
    year_folder: Series[str] = pa.Field(nullable=True)

    class Config:
        strict = True
        coerce = True


class WeatherObservation(DataFrameModel):
    station_code: Series[str] = pa.Field(coerce=True)
    source_file: Series[str] = pa.Field(coerce=True)
    year_folder: Series[str] = pa.Field(nullable=True)

    date: Series[str] = pa.Field(coerce=True)
    time_utc: Series[str] = pa.Field(coerce=True)
    hourly_precipitation: Series[float] = pa.Field(nullable=True)
    station_pressure: Series[float] = pa.Field(nullable=True)
    pressure_max_previous_hour: Series[float] = pa.Field(nullable=True)
    pressure_min_previous_hour: Series[float] = pa.Field(nullable=True)
    global_radiation: Series[float] = pa.Field(nullable=True)
    air_temperature: Series[float] = pa.Field(nullable=True)
    dew_point_temperature: Series[float] = pa.Field(nullable=True)
    max_temperature_previous_hour: Series[float] = pa.Field(nullable=True)
    min_temperature_previous_hour: Series[float] = pa.Field(nullable=True)
    max_dew_point_previous_hour: Series[float] = pa.Field(nullable=True)
    min_dew_point_previous_hour: Series[float] = pa.Field(nullable=True)
    max_relative_humidity_previous_hour: Series[float] = pa.Field(
        nullable=True
    )
    min_relative_humidity_previous_hour: Series[float] = pa.Field(
        nullable=True
    )
    relative_humidity: Series[float] = pa.Field(nullable=True)
    wind_direction_degrees: Series[float] = pa.Field(nullable=True)
    wind_gust: Series[float] = pa.Field(nullable=True)
    wind_speed: Series[float] = pa.Field(nullable=True)

    class Config:
        strict = True
        coerce = True


WeatherStationDataFrame = DataFrame[WeatherStation]
WeatherObservationDataFrame = DataFrame[WeatherObservation]
