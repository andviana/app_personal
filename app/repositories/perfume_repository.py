from typing import List
from app.repositories.base_repository import BaseRepository
from app.models import Perfume

class PerfumeRepository(BaseRepository):
    def __init__(self):
        super().__init__(Perfume)

    def list_ordered_by_nome(self) -> List[Perfume]:
        return self.list_all(order_by=self.model.nome)
