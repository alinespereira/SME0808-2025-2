from sqlalchemy.engine import ScalarResult
from sqlmodel import select

from .base import BaseDAO
from ..models import State


class StateDAO(BaseDAO[State]):
    model = State

    def get_by_code(self, code: str) -> State | None:
        statement = select(State).where(State.code == code)
        result: ScalarResult[State] = self.session.exec(statement)
        return result.first()

    def list_by_region(self, region_id: int) -> list[State]:
        statement = select(State).where(State.region_id == region_id)
        result: ScalarResult[State] = self.session.exec(statement)
        return list(result)
