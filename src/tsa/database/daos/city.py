from sqlalchemy.engine import ScalarResult
from sqlmodel import select

from ..models import City
from .base import BaseDAO


class CityDAO(BaseDAO[City]):
    model = City

    def get_by_name(self, name: str, *, state_id: int) -> City | None:
        statement = select(City).where(
            City.name == name, City.state_id == state_id
        )
        result: ScalarResult[City] = self.session.exec(statement)
        return result.first()

    def list_by_state(self, state_id: int) -> list[City]:
        statement = select(City).where(City.state_id == state_id)
        result: ScalarResult[City] = self.session.exec(statement)
        return list(result)
