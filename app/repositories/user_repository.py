from app.repositories.base_repository import BaseRepository
from app.models import User

class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def find_by_username(self, username: str) -> User:
        return self.find_one_by(username=username)

    def list_all_users(self):
        return self.model.query.order_by(self.model.username).all()

