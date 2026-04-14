from app import db

class BaseRepository:
    def __init__(self, model):
        self.model = model

    def get_by_id(self, id):
        return self.model.query.get(id)

    def get_or_404(self, id):
        return self.model.query.get_or_404(id)

    def list_all(self, order_by=None):
        query = self.model.query
        if order_by is not None:
            query = query.order_by(order_by)
        return query.all()

    def add(self, entity):
        db.session.add(entity)
        return entity

    def delete(self, entity):
        db.session.delete(entity)

    def commit(self):
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def flush(self):
        db.session.flush()
