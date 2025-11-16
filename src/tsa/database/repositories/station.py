from ..daos import StationDAO
from ..models import Station
from .base import BaseRepository


class StationRepository(BaseRepository[Station, StationDAO]):
    dao_class = StationDAO

    def get_by_code(self, code: str) -> Station | None:
        return self.dao.get_by_code(code)

    def ensure(
        self,
        *,
        code: str,
        latitude: float,
        longitude: float,
        altitude: float,
        city_id: int,
        state_id: int,
    ) -> Station:
        station: Station | None = self.dao.get_by_code(code)
        data: dict[str, float | int] = {
            "latitude": latitude,
            "longitude": longitude,
            "altitude": altitude,
            "city_id": city_id,
            "state_id": state_id,
        }
        if station:
            return self.dao.update(station, **data)
        return self.dao.create(code=code, **data)
