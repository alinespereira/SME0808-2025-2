from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

if __package__ in {None, ""}:
    project_root = Path(__file__).resolve().parents[2]
    src_dir = project_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

import click
import pandas as pd

from tsa import settings
from tsa.database.models import WeatherObservation, WeatherObservationDataFrame, WeatherStation, WeatherStationDataFrame


@click.command()
@click.option(
    "--database",
    "-d",
    type=click.Path(path_type=Path, dir_okay=False),
    default=settings.data_path / "weather.db",
    show_default=True,
    help="SQLite database generated pelo comando build-db.",
)
@click.option(
    "--stations-table",
    "-s",
    default="weather_stations",
    show_default=True,
    help="Nome da tabela com metadados das estações.",
)
@click.option(
    "--observations-table",
    "-t",
    default="weather_observations",
    show_default=True,
    help="Nome da tabela com observações horárias.",
)
@click.option(
    "--limit",
    "-l",
    default=5,
    show_default=True,
    help="Quantidade de linhas de cada tabela para exibir após validação.",
)
def main(database: Path, stations_table: str, observations_table: str, limit: int) -> None:
    """Ler o banco gerado, validar usando Pandera e imprimir algumas linhas."""
    if not database.exists():
        raise FileNotFoundError(f"Banco de dados não encontrado em {database}")

    with sqlite3.connect(database) as connection:
        stations_raw = pd.read_sql(f"SELECT * FROM {stations_table}", connection)
        observations_raw = pd.read_sql(f"SELECT * FROM {observations_table}", connection)

    stations_validated: WeatherStationDataFrame = WeatherStation.validate(stations_raw)
    observations_validated: WeatherObservationDataFrame = WeatherObservation.validate(observations_raw)

    click.echo("\nEstações validadas:")
    click.echo(stations_validated.head(limit).to_string(index=False))

    click.echo("\nObservações validadas:")
    click.echo(observations_validated.head(limit).to_string(index=False))


if __name__ == "__main__":
    main()
