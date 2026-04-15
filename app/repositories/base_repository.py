from typing import TypeVar, Type, List, Optional, Any, Generic
from app import db
from flask_sqlalchemy.model import Model

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: Any) -> Optional[T]:
        return db.session.get(self.model, id)

    def get_or_404(self, id: Any) -> T:
        entity = db.session.get(self.model, id)
        if entity is None:
            from flask import abort
            abort(404)
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
        except Exception as e:
            db.session.rollback()
            raise e

    def flush(self) -> None:
        db.session.flush()

