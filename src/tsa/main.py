from sqlmodel import Session, text
from tsa.database.connector import Connector
from tsa.settings import Settings

def main() -> None:

    settings = Settings()
    commector = Connector(settings=settings.db)
    with Session(commector.engine) as session:
        stmt = text("SELECT 1, 2")
        result = session.exec(stmt)
        print(f"Database connection test result: {result.all()}")