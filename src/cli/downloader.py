from pathlib import Path
import zipfile

from tsa import settings

import click
import httpx

ALL_YEARS: int = -1


def download_file(url: str, dest_path: Path) -> None:
    """Download a file from a URL to a local destination."""
    with httpx.stream("GET", url) as response:
        response.raise_for_status()
        with open(dest_path, "wb") as file:
            for chunk in response.iter_bytes():
                file.write(chunk)

def unzip_file(zip_path: Path, extract_to: Path) -> None:
    """Unzip a zip file to a specified directory."""    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def download_and_unzip(url: str) -> None:
    file_name = Path(url).name
    dest_path = settings.data_path / file_name
    download_file(url, dest_path)
    unzip_file(dest_path, settings.data_path)
    dest_path.unlink()

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
            years = [click.prompt("Por favor, insira o ano desejado (2000-2025)", type=int)]
    else:
        years = [year]

    for year in years:
        url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
        download_and_unzip(url)
        print("Todos os arquivos foram baixados e extraídos.")
        return
