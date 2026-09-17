from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import selectinload
from app.repositories.base_repository import BaseRepository
from app.models import Bookmark, BookmarkCategory

class BookmarkRepository(BaseRepository):
    def __init__(self):
        super().__init__(Bookmark)

    def list_user_bookmarks(self, user_id: int) -> List[Bookmark]:
        return self.model.query.options(
            selectinload(self.model.categories),
            selectinload(self.model.shared_users)
        ).filter(
            or_(
                self.model.owner_id == user_id,
                self.model.shared_users.any(id=user_id)
            )
        ).order_by(self.model.data_criacao.desc()).all()

class BookmarkCategoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(BookmarkCategory)

    def list_ordered_by_nome(self) -> List[BookmarkCategory]:
        return self.list_all(order_by=self.model.nome)

    def find_by_ids(self, category_ids: List[int]) -> List[BookmarkCategory]:
        return self.model.query.filter(self.model.id.in_(category_ids)).all()
