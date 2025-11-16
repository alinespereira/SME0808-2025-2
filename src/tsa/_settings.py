from pathlib import Path

from pydantic import BaseModel, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_PATH: Path = Path(__file__).parent.parent.parent.resolve()


class DatabaseSettings(BaseModel):
    echo_sql: bool = False
    drivername: str = ""
    host: str = "localhost"
    port: PositiveInt = 5432
    database: str = "postgres"
    username: str = ""
    password: SecretStr = Field(default=SecretStr(""), repr=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_PATH / ".env",
        env_nested_delimiter="__",
        frozen=True,
    )

    data_path: Path = PROJECT_PATH / "data"
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    station: str = "A711"


settings = Settings()
