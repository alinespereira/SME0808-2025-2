from ..daos import CityDAO
from ..models import City
from .base import BaseRepository


class CityRepository(BaseRepository[City, CityDAO]):
    dao_class = CityDAO

    def ensure(self, *, name: str, state_id: int) -> City:
        city: City | None = self.dao.get_by_name(name, state_id=state_id)
        if city:
            return city
        return self.dao.create(name=name, state_id=state_id)
