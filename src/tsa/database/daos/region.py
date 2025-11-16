from sqlalchemy.engine import ScalarResult
from sqlmodel import select

from ..models import Region
from .base import BaseDAO


class RegionDAO(BaseDAO[Region]):
    model = Region

    def get_by_code(self, code: str) -> Region | None:
        statement = select(Region).where(Region.code == code)
        result: ScalarResult[Region] = self.session.exec(statement)
        return result.first()
