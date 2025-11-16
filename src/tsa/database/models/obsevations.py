import datetime as dt
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class Observation(SQLModel, table=True):
    __tablename__ = "observations"
    __table_args__ = {"schema": "inmet"}

    id: Optional[int] = Field(default=None, primary_key=True)
    station_id: int = Field(foreign_key="inmet.stations.id")
    datetime: dt.datetime
    precipitation: Optional[float] = Field(
        default=None, description="Precipitação total, horário (mm)"
    )
    atmospheric_pressure: Optional[float] = Field(
        default=None,
        description="Pressão atmosférica ao nível da estação, horária (mB)",
    )
    prev_max_pressure: Optional[float] = Field(
        default=None,
        description="Pressão atmosférica max.na hora ant. (AUT) (mB)",
    )
    prev_min_pressure: Optional[float] = Field(
        default=None,
        description="Pressão atmosférica min. na hora ant. (AUT) (mB)",
    )
    global_radiation: Optional[float] = Field(
        default=None, description="Radiação global (Kj/m²)"
    )
    air_temperature: Optional[float] = Field(
        default=None,
        description="Temperatura do ar - bulbo seco, horária (°C)",
    )
    dew_point_temperature: Optional[float] = Field(
        default=None, description="Temperatura do ponto de orvalho (°C)"
    )
    max_temperature: Optional[float] = Field(
        default=None, description="Temperatura máxima na hora ant. (AUT) (°C)"
    )
    min_temperature: Optional[float] = Field(
        default=None, description="Temperatura mínima na hora ant. (AUT) (°C)"
    )
    max_dew_point_temperature: Optional[float] = Field(
        default=None,
        description="Temperatura orvalho max. na hora ant. (AUT) (°C)",
    )
    min_dew_point_temperature: Optional[float] = Field(
        default=None,
        description="Temperatura orvalho min. na hora ant. (AUT) (°C)",
    )
    max_relative_humidity: Optional[float] = Field(
        default=None, description="Umidade rel. max. na hora ant. (AUT) (%)"
    )
    min_relative_humidity: Optional[float] = Field(
        default=None, description="Umidade rel. min. na hora ant. (AUT) (%)"
    )
    relative_humidity: Optional[float] = Field(
        default=None, description="Umidade relativa do ar, horaria (%)"
    )
    wind_direction: Optional[float] = Field(
        default=None, description="Vento, direção horaria (gr) (° (gr))"
    )
    max_wind_gust: Optional[float] = Field(
        default=None, description="Vento, rajada maxima (m/s)"
    )
    wind_speed: Optional[float] = Field(
        default=None, description="Vento, velocidade horaria (m/s)"
    )
    created_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(tz=dt.timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(tz=dt.timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    station: "Station" = Relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="observations"
    )
