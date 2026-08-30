from typing import TypeVar, Type, List, Optional, Any, Generic
from app import db
from app.exceptions import NotFoundError
from flask_sqlalchemy.model import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: Any) -> Optional[T]:
        return db.session.get(self.model, id)

    def get_or_404(self, id: Any) -> T:
        entity = self.get_by_id(id)
        if entity is None:
            raise NotFoundError(f"{self.model.__name__} com id={id!r} não encontrado.")
        return entity

    def find_one_by(self, **kwargs) -> Optional[T]:
        return db.session.query(self.model).filter_by(**kwargs).first()

    def find_one_or_404(self, **kwargs) -> T:
        entity = self.find_one_by(**kwargs)
        if entity is None:
            raise NotFoundError(f"{self.model.__name__} não encontrado para {kwargs!r}.")
        return entity

    def list_all(self, order_by: Any = None, options: List[Any] = None) -> List[T]:
        """
        List all records with optional ordering and eager loading options.
        Example options: [joinedload(Model.relation)]
        """
        query = db.session.query(self.model)
        if options:
            for option in options:
                query = query.options(option)
        if order_by is not None:
            query = query.order_by(order_by)
        return query.all()

    def add(self, entity: T) -> T:
        db.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        db.session.delete(entity)

    def commit(self) -> None:
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

    def flush(self) -> None:
        db.session.flush()

    def rollback(self) -> None:
        db.session.rollback()
