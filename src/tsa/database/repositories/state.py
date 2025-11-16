from ..daos import StateDAO
from ..models import State
from .base import BaseRepository


class StateRepository(BaseRepository[State, StateDAO]):
    dao_class = StateDAO

    def ensure(self, *, code: str, name: str | None = None, region_id: int) -> State:
        state: State | None = self.dao.get_by_code(code)
        if state:
            updates: dict[str, int | str] = {}
            if state.region_id != region_id:
                updates["region_id"] = region_id
            if name and state.name != name:
                updates["name"] = name
            return self.dao.update(state, **updates) if updates else state
        return self.dao.create(code=code, name=name or code, region_id=region_id)
