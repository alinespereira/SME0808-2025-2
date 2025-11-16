import zipfile
from pathlib import Path

import click
import httpx

from tsa import settings

ALL_YEARS: int = -1


def download_file(url: str, dest_path: Path) -> None:
    """Download a file from a URL to a local destination."""
    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)


def unzip_file(zip_path: Path, extract_to: Path) -> None:
    """Unzip only the files that match the configured station name."""
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        station_files = [
            zip_info
            for zip_info in zip_ref.infolist()
            if settings.station in zip_info.filename
        ]
        if not station_files:
            raise FileNotFoundError(
                f"Arquivo com estação {settings.station} não encontrado em {zip_path.name}"
            )
        for zip_info in station_files:
            file_name = Path(zip_info.filename).stem
            zip_ref.extract(zip_info, extract_to / file_name)


def download_and_unzip(url: str) -> None:
    file_name = Path(url).name
    dest_path = settings.data_path / file_name
    try:
        download_file(url, dest_path)
        unzip_file(dest_path, settings.data_path)
    finally:
        dest_path.unlink()
    # move all csv/CSV files to the data_path root
    for extracted_file in settings.data_path.glob(
        "**/*.csv", case_sensitive=False
    ):
        extracted_file.rename(settings.data_path / extracted_file.name)
    # remove empty directories
    for dir_path in settings.data_path.glob("**/"):
        try:
            dir_path.rmdir()
        except OSError:
            pass


@click.command()
@click.option(
    "--year",
    "-y",
    type=int,
    prompt="Digite o ano desejado",
    default=ALL_YEARS,
    show_default=False,
)
def main(year: int = ALL_YEARS) -> None:
    years: list[int]
    if year == ALL_YEARS:
        download_all: bool = click.prompt(
            "Deseja baixar todos os anos disponíveis?",
            type=bool,
            default=False,
            show_default=False,
        )
        if download_all:
            years = range(2000, 2026)
        else:
            years = [
                click.prompt(
                    "Por favor, insira o ano desejado (2000-2025)", type=int
                )
            ]
    else:
        years = [year]

    for year in years:
        try:
            url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
            download_and_unzip(url)
        except FileNotFoundError:
            continue

    print("Todos os arquivos foram baixados e extraídos.")
