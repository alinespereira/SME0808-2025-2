from collections.abc import Generator
from contextlib import contextmanager
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, PostgresDsn, computed_field
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from .._settings import DatabaseSettings


class Connector(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True,
        arbitrary_types_allowed=True,
    )
    settings: DatabaseSettings

    @computed_field
    @property  # type: ignore[prop-decorator]
    def url(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme=self.settings.drivername,
            username=self.settings.username,
            password=self.settings.password.get_secret_value(),
            host=self.settings.host,
            port=self.settings.port,
            path=self.settings.database,
        )

    @computed_field
    @property  # type: ignore[prop-decorator]
    def engine(self) -> Engine:
        return create_engine(url=str(self.url), echo=self.settings.echo_sql)

    @contextmanager
    def get_session(self) -> Generator[Session]:
        """Context manager to provide a database engine."""
        with Session(self.engine) as session:
            yield session
