from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel


class Region(SQLModel, table=True):
    __tablename__ = "regions"
    __table_args__ = {"schema": "inmet"}

    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(description="Código da região")
    name: str = Field(description="Nome da região")
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

    states: list["State"] = Relationship(  # type: ignore[name-defined] # noqa: F821
        back_populates="region"
    )
