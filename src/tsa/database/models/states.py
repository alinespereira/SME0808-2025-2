from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class State(SQLModel, table=True):
    __tablename__ = "states"
    __table_args__ = {"schema": "inmet"}

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(description="Código da estação")
    name: str = Field(description="Nome da estação")
    region_id: int = Field(
        description="ID da região da estação", foreign_key="inmet.regions.id"
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

    region: "Region" = Relationship(back_populates="states")  # type: ignore[name-defined] # noqa: F821
    cities: list["City"] = Relationship(back_populates="state")  # type: ignore[name-defined] # noqa: F821
    stations: list["Station"] = Relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="state"
    )
