from typing import List, Any
from app.repositories.list_repository import ListRepository, ItemListaRepository, GrupoItemRepository, TipoListaRepository
from app.models import Lista, ItemLista, TipoLista, GrupoItem, User
from app.services.log_service import LogService

class ListService:
    @staticmethod
    def can_read(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id or any(u.id == current_user.id for u in lista.shared_users)

    @staticmethod
    def can_write(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id or any(u.id == current_user.id for u in lista.shared_users)

    @staticmethod
    def can_manage(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id

    @staticmethod
    def get_lists_data(current_user: Any, is_active: bool = True):
        repo_listas = ListRepository()
        repo_tipos = TipoListaRepository()
        return repo_listas.list_user_lists(current_user.id, is_active=is_active), repo_tipos.list_ordered_by_denominacao()

    @staticmethod
    def create_list(denominacao: str, tipo_id: Any, current_user: Any):
        if denominacao:
            repo = ListRepository()
            nova_lista = Lista(
                denominacao=denominacao.upper(), 
                tipo_id=tipo_id if tipo_id else None,
                owner_id=current_user.id,
                is_active=True
            )
            repo.add(nova_lista)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_CREATED', f'ID: {nova_lista.id} | TITLE: {denominacao}')
            return nova_lista
        return None

    @staticmethod
    def delete_list(id: int, current_user: Any):
        repo = ListRepository()
        lista = repo.get_or_404(id)
        if not ListService.can_manage(lista, current_user):
            raise PermissionError("Apenas o proprietário pode excluir esta lista.")
        denominacao = lista.denominacao
        repo.delete(lista)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_DELETED', f'ID: {id} | TITLE: {denominacao}')
        return denominacao

    @staticmethod
    def archive_list(id: int, current_user: Any):
        repo = ListRepository()
        lista = repo.get_or_404(id)
        if not ListService.can_manage(lista, current_user):
            raise PermissionError("Apenas o proprietário pode arquivar esta lista.")
        lista.is_active = False
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_ARCHIVED', f'ID: {id}')
        return lista

    @staticmethod
    def reactivate_list(id: int, current_user: Any):
        repo = ListRepository()
        lista = repo.get_or_404(id)
        if not ListService.can_manage(lista, current_user):
            raise PermissionError("Apenas o proprietário pode reativar esta lista.")
        lista.is_active = True
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_REACTIVATED', f'ID: {id}')
        return lista

    @staticmethod
    def share_list(id: int, user_ids: List[int], current_user: Any):
        repo = ListRepository()
        lista = repo.get_or_404(id)
        if not ListService.can_manage(lista, current_user):
            raise PermissionError("Apenas o proprietário pode compartilhar esta lista.")
        
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
        lista.shared_users = [u for u in users if u.id != lista.owner_id]
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_SHARED', f'ID: {id} | SHARED_WITH: {[u.username for u in lista.shared_users]}')
        return lista

    @staticmethod
    def get_list_detail(id: int, current_user: Any):
        repo_lista = ListRepository()
        repo_grupos = GrupoItemRepository()
        lista = repo_lista.get_or_404(id)
        if not ListService.can_read(lista, current_user):
            raise PermissionError("Sem permissão para visualizar esta lista.")
        grupos = repo_grupos.list_ordered_by_denominacao()
        lista.itens.sort(key=lambda x: (x.status, x.item))
        return lista, grupos

    @staticmethod
    def create_list_item(lista_id: int, item_text: str, grupo_id: Any, valor: Any, link: Any, current_user: Any):
        repo_lista = ListRepository()
        lista = repo_lista.get_or_404(lista_id)
        if not ListService.can_write(lista, current_user):
            raise PermissionError("Sem permissão para adicionar itens a esta lista.")
        
        if item_text:
            repo = ItemListaRepository()
            if not grupo_id:
                repo_g = GrupoItemRepository()
                outros = repo_g.find_by_denominacao('OUTROS')
                if not outros:
                    outros = GrupoItem(denominacao='OUTROS')
                    repo_g.add(outros)
                    repo_g.commit()
                grupo_id = outros.id
            
            novo_item = ItemLista(
                lista_id=lista_id,
                item=item_text.upper(),
                grupo_id=grupo_id if grupo_id else None,
                valor=valor if valor else None,
                link=link if link else None
            )
            repo.add(novo_item)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_ITEM_CREATED', f'LIST_ID: {lista_id} | ITEM: {item_text}')
            return novo_item
        return None

    @staticmethod
    def update_list_item(item_id: int, item_text: str, grupo_id: Any, valor: Any, link: Any, current_user: Any):
        repo = ItemListaRepository()
        item = repo.get_or_404(item_id)
        if not ListService.can_write(item.lista, current_user):
            raise PermissionError("Sem permissão para editar itens desta lista.")
        if item_text:
            item.item = item_text.upper()
            item.grupo_id = grupo_id if grupo_id else None
            item.valor = valor if valor else None
            item.link = link if link else None
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_ITEM_UPDATED', f'ID: {item_id} | ITEM: {item_text}')
            return item
        return None

    @staticmethod
    def toggle_item_check(item_id: int, checked: Any, current_user: Any):
        repo = ItemListaRepository()
        item = repo.get_or_404(item_id)
        if not ListService.can_write(item.lista, current_user):
            raise PermissionError("Sem permissão para alterar itens desta lista.")
        if checked is None:
            item.status = not item.status
        else:
            item.status = checked
        repo.commit()
        log_status = "COMPRADO" if item.status else "PENDENTE"
        LogService.log_action(current_user.username, 'LIST_ITEM_TOGGLE', f'ID: {item_id} | NEW_STATUS: {log_status}')
        return item

    @staticmethod
    def delete_item(item_id: int, current_user: Any):
        repo = ItemListaRepository()
        item = repo.get_or_404(item_id)
        if not ListService.can_write(item.lista, current_user):
            raise PermissionError("Sem permissão para excluir itens desta lista.")
        item_text = item.item
        repo.delete(item)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_ITEM_DELETED', f'ID: {item_id}')
        return item_text

    @staticmethod
    def create_list_type(denominacao: str, current_user: Any):
        if denominacao:
            repo = TipoListaRepository()
            novo_tipo = TipoLista(denominacao=denominacao.upper())
            repo.add(novo_tipo)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_TYPE_CREATED', f'NAME: {denominacao}')
            return novo_tipo
        return None

    @staticmethod
    def create_item_group(denominacao: str, current_user: Any):
        if denominacao:
            repo = GrupoItemRepository()
            novo_grupo = GrupoItem(denominacao=denominacao.upper())
            repo.add(novo_grupo)
            repo.commit()
            LogService.log_action(current_user.username, 'ITEM_GROUP_CREATED', f'NAME: {denominacao}')
            return novo_grupo
        return None

