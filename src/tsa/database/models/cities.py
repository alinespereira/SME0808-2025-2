from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class City(SQLModel, table=True):
    __tablename__ = "cities"
    __table_args__ = {"schema": "inmet"}

    id: int = Field(default=None, primary_key=True)
    name: str
    state_id: int = Field(foreign_key="inmet.states.id")
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

    state: "State" = Relationship(back_populates="cities")  # type: ignore[name-defined] # noqa: F821
    stations: list["Station"] = Relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="city"
    )
