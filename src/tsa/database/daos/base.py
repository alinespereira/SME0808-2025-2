from typing import Any, Generic, Iterable, Sequence, TypeVar

from sqlalchemy.engine import ScalarResult
from sqlmodel import Session, SQLModel, select

TModel = TypeVar("TModel", bound=SQLModel)


class BaseDAO(Generic[TModel]):
    """Low-level helper responsible for interacting with a single SQLModel."""

    model: type[TModel]

    def __init__(self, session: Session):
        self.session = session

    def get(self, obj_id: Any) -> TModel | None:
        return self.session.get(self.model, obj_id)

    def list(self, *, limit: int | None = None) -> list[TModel]:
        statement = select(self.model)
        if limit:
            statement = statement.limit(limit)
        result: ScalarResult[TModel] = self.session.exec(statement)
        return list(result)

    def create(self, **data: Any) -> TModel:
        instance = self.model(**data)  # type: ignore[arg-type]
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def create_many(self, instances: Iterable[TModel]) -> Sequence[TModel]:
        instances = list(instances)
        if not instances:
            return instances
        self.session.add_all(instances)
        self.session.commit()
        for instance in instances:
            self.session.refresh(instance)
        return instances

    def update(self, instance: TModel, **data: Any) -> TModel:
        for field, value in data.items():
            setattr(instance, field, value)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def delete(self, instance: TModel) -> None:
        self.session.delete(instance)
        self.session.commit()
