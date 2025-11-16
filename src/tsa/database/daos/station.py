from sqlalchemy.engine import ScalarResult
from sqlmodel import select

from .base import BaseDAO
from ..models import Station


class StationDAO(BaseDAO[Station]):
    model = Station

    def get_by_code(self, code: str) -> Station | None:
        statement = select(Station).where(Station.code == code)
        result: ScalarResult[Station] = self.session.exec(statement)
        return result.first()

    def list_by_city(self, city_id: int) -> list[Station]:
        statement = select(Station).where(Station.city_id == city_id)
        result: ScalarResult[Station] = self.session.exec(statement)
        return list(result)
