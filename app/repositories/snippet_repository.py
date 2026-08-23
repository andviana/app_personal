from typing import List, Optional
from app.repositories.base_repository import BaseRepository
from app.models import Snippet, Tag, SnippetTag

class SnippetRepository(BaseRepository):
    def __init__(self):
        super().__init__(Snippet)

    def search_snippets(self, search: Optional[str] = None) -> List[Snippet]:
        if search:
            if search.startswith('#'):
                tag_name = search[1:].upper()
                return self.model.query.join(self.model.tags).filter(Tag.denominacao == tag_name).all()
            
            return self.model.query.filter(
                (self.model.titulo.ilike(f'%{search}%')) | 
                (self.model.conteudo.ilike(f'%{search}%')) |
                (self.model.descricao.ilike(f'%{search}%'))
            ).all()
        
        return self.list_all(order_by=self.model.data_criacao.desc())

class TagRepository(BaseRepository):
    def __init__(self):
        super().__init__(Tag)

    def list_ordered_by_denominacao(self) -> List[Tag]:
        return self.list_all(order_by=self.model.denominacao)

    def find_by_denominacao(self, denominacao: str) -> Optional[Tag]:
        return self.find_one_by(denominacao=denominacao)

class SnippetTagRepository(BaseRepository):
    def __init__(self):
        super().__init__(SnippetTag)

    def delete_by_tag_id(self, tag_id: int) -> None:
        self.model.query.filter_by(tag_id=tag_id).delete()
