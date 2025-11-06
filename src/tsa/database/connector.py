from pydantic import BaseModel, ConfigDict, computed_field, PostgresDsn
from sqlmodel import create_engine
from sqlalchemy import Engine
from tsa.settings import DatabaseSettings

class Connector(BaseModel):
    model_config = ConfigDict(
        frozem=True,
        arbitrary_types_allowed=True,
    )
    settings: DatabaseSettings

    @computed_field
    @property
    def url(self) -> PostgresDsn:
        PostgresDsn
        return PostgresDsn.build(
            scheme=self.settings.drivername,
            username=self.settings.username,
            password=self.settings.password.get_secret_value(),
            host=self.settings.host,
            port=self.settings.port,
            path=self.settings.database,
        )

    @computed_field
    @property
    def engine(self) -> Engine:
        return create_engine(
            url=str(self.url), echo=self.settings.echo_sql
        )