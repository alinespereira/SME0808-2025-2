from ..daos import RegionDAO
from ..models import Region
from .base import BaseRepository


class RegionRepository(BaseRepository[Region, RegionDAO]):
    dao_class = RegionDAO

    def ensure(self, *, code: str, name: str | None = None) -> Region:
        region: Region | None = self.dao.get_by_code(code)
        if region:
            if name and region.name != name:
                return self.dao.update(region, name=name)
            return region
        return self.dao.create(code=code, name=name or code)
