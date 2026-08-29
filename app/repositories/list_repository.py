from typing import List, Optional
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models import Lista, ItemLista, GrupoItem, TipoLista

class ListRepository(BaseRepository):
    def __init__(self):
        super().__init__(Lista)

    def list_ordered_by_denominacao(self) -> List[Lista]:
        return self.list_all(order_by=self.model.denominacao)

    def list_simple_lists(self) -> List[Lista]:
        return self.model.query.filter(self.model.tipo_id == None).order_by(self.model.denominacao).all()

    def list_user_lists(self, user_id: int, is_active: bool = True) -> List[Lista]:
        return self.model.query.filter(
            self.model.tipo_id != None,
            self.model.is_active == is_active,
            or_(
                self.model.owner_id == user_id,
                self.model.shared_users.any(id=user_id)
            )
        ).order_by(self.model.denominacao).all()

    def list_user_simple_lists(self, user_id: int, is_active: bool = True) -> List[Lista]:
        return self.model.query.filter(
            self.model.tipo_id == None,
            self.model.is_active == is_active,
            or_(
                self.model.owner_id == user_id,
                self.model.shared_simple_users.any(id=user_id)
            )
        ).order_by(self.model.denominacao).all()


class ItemListaRepository(BaseRepository):
    def __init__(self):
        super().__init__(ItemLista)

class GrupoItemRepository(BaseRepository):
    def __init__(self):
        super().__init__(GrupoItem)

    def list_ordered_by_denominacao(self) -> List[GrupoItem]:
        return self.list_all(order_by=self.model.denominacao)

    def find_by_denominacao(self, denominacao: str) -> Optional[GrupoItem]:
        return self.find_one_by(denominacao=denominacao)

class TipoListaRepository(BaseRepository):
    def __init__(self):
        super().__init__(TipoLista)

    def list_ordered_by_denominacao(self) -> List[TipoLista]:
        return self.list_all(order_by=self.model.denominacao)
