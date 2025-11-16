from datetime import datetime
from typing import Iterable

from ..daos import ObservationDAO
from ..models import Observation
from .base import BaseRepository


class ObservationRepository(BaseRepository[Observation, ObservationDAO]):
    dao_class = ObservationDAO

    def upsert_batch(self, observations: Iterable[Observation]) -> list[Observation]:
        """Insert a batch of observations, replacing duplicates by station/time."""
        persisted: list[Observation] = []
        for obs in observations:
            existing: Observation | None = self.dao.get_by_station_and_time(
                obs.station_id, obs.datetime
            )
            if existing:
                updated: Observation = self.dao.update(
                    existing,
                    precipitation=obs.precipitation,
                    atmospheric_pressure=obs.atmospheric_pressure,
                    prev_max_pressure=obs.prev_max_pressure,
                    prev_min_pressure=obs.prev_min_pressure,
                    global_radiation=obs.global_radiation,
                    air_temperature=obs.air_temperature,
                    dew_point_temperature=obs.dew_point_temperature,
                    max_temperature=obs.max_temperature,
                    min_temperature=obs.min_temperature,
                    max_dew_point_temperature=obs.max_dew_point_temperature,
                    min_dew_point_temperature=obs.min_dew_point_temperature,
                    max_relative_humidity=obs.max_relative_humidity,
                    min_relative_humidity=obs.min_relative_humidity,
                    relative_humidity=obs.relative_humidity,
                    wind_direction=obs.wind_direction,
                    max_wind_gust=obs.max_wind_gust,
                    wind_speed=obs.wind_speed,
                )
                persisted.append(updated)
            else:
                persisted.append(self.dao.create(**obs.model_dump(exclude={"id"})))
        return persisted

    def find_for_station(
        self, station_id: int, *, limit: int | None = None
    ) -> list[Observation]:
        return self.dao.list_by_station(station_id, limit=limit)
