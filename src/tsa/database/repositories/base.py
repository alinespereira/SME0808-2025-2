from typing import Any, Generic, TypeVar

from sqlmodel import Session, SQLModel

from ..daos import BaseDAO


TModel = TypeVar("TModel", bound=SQLModel)
TDAO = TypeVar("TDAO", bound=BaseDAO[Any])


class BaseRepository(Generic[TModel, TDAO]):
    """High-level helper that wraps a DAO and exposes domain semantics."""

    dao_class: type[TDAO]

    def __init__(self, session: Session, dao: TDAO | None = None):
        self.session = session
        if dao is None:
            dao = self.dao_class(session)
        self.dao: TDAO = dao

    def get(self, obj_id: Any) -> TModel | None:
        return self.dao.get(obj_id)

    def list(self, *, limit: int | None = None) -> list[TModel]:
        return self.dao.list(limit=limit)
