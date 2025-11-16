from datetime import datetime

from sqlalchemy.engine import ScalarResult
from sqlmodel import select

from ..models import Observation
from .base import BaseDAO


class ObservationDAO(BaseDAO[Observation]):
    model = Observation

    def list_by_station(
        self, station_id: int, *, limit: int | None = None
    ) -> list[Observation]:
        statement = (
            select(Observation)
            .where(Observation.station_id == station_id)
            .order_by(Observation.datetime)  # type: ignore[arg-type]
        )
        if limit:
            statement = statement.limit(limit)
        result: ScalarResult[Observation] = self.session.exec(statement)
        return list(result)

    def get_by_station_and_time(
        self, station_id: int, dt: datetime
    ) -> Observation | None:
        statement = select(Observation).where(
            Observation.station_id == station_id,
            Observation.datetime == dt,
        )
        result: ScalarResult[Observation] = self.session.exec(statement)
        return result.first()
