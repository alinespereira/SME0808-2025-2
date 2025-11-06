from pathlib import Path
from pydantic import BaseModel, Field, PositiveInt, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_PATH: Path = Path(__file__).parent.parent.parent.resolve()

class DatabaseSettings(BaseModel):
    echo_sql: bool = False
    drivername: str
    host: str
    port: PositiveInt
    database: str
    username: str
    password: SecretStr = Field(repr=False)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        frozen=True,
    )

    data_path: Path = PROJECT_PATH / 'data'
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)