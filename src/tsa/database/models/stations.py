from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class Station(SQLModel, table=True):
    __tablename__ = "stations"
    __table_args__ = {"schema": "inmet"}

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(description="Código da estação", unique=True)
    latitude: float = Field(description="Latitude da estação")
    longitude: float = Field(description="Longitude da estação")
    altitude: float = Field(description="Altitude da estação (m)")
    city_id: int = Field(
        description="Cidade onde a estação está localizada",
        foreign_key="inmet.cities.id",
    )
    state_id: int = Field(
        description="Estado onde a estação está localizada",
        foreign_key="inmet.states.id",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
    )

    observations: list["Observation"] = Relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="station"
    )
    city: "City" = Relationship(back_populates="stations")  # type: ignore[name-defined] # noqa: F821
    state: "State" = Relationship(back_populates="stations")  # type: ignore[name-defined] # noqa: F821
