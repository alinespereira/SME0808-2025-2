from importlib import import_module
from pkgutil import iter_modules

import click
from sqlmodel import Session, SQLModel, text

from tsa import settings
from tsa.database import models
from tsa.database.connector import Connector


def _load_models() -> None:
    """Ensure every model under tsa.database.model is imported."""
    prefix = f"{models.__name__}."
    for module in iter_modules(models.__path__, prefix):
        import_module(module.name)


@click.command()
@click.option(
    "--drop/--no-drop",
    default=False,
    show_default=True,
    help="Se deve dropar as tabelas existentes antes de criar novas.",
)
def main(drop: bool) -> None:
    """Create every table declared in the SQLModel models."""
    connector = Connector(settings=settings.db)

    _load_models()
    with Session(connector.engine) as session:
        session.exec(text("CREATE SCHEMA IF NOT EXISTS inmet"))
        session.commit()
    if drop:
        SQLModel.metadata.drop_all(bind=connector.engine)
    SQLModel.metadata.create_all(bind=connector.engine)
    click.echo("Tabelas criadas com sucesso.")
