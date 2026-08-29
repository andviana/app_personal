from typing import List, Any
from app.repositories.list_repository import ListRepository, ItemListaRepository
from app.models import Lista, ItemLista, User
from app.services.log_service import LogService

class SimpleListService:
    @staticmethod
    def can_read(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id or any(u.id == current_user.id for u in lista.shared_simple_users)

    @staticmethod
    def can_write(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id or any(u.id == current_user.id for u in lista.shared_simple_users)

    @staticmethod
    def can_manage(lista: Lista, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return lista.owner_id == current_user.id

    @staticmethod
    def get_all_lists(current_user: Any, is_active: bool = True):
        repo = ListRepository()
        return repo.list_user_simple_lists(current_user.id, is_active=is_active)

    @staticmethod
    def get_list_by_id(lista_id: int, current_user: Any):
        repo = ListRepository()
        lista = repo.get_by_id(lista_id)
        if lista:
            if not SimpleListService.can_read(lista, current_user):
                return None
            lista.itens.sort(key=lambda x: (x.status, x.item))
        return lista

    @staticmethod
    def create_list(nome: str, current_user: Any):
        repo = ListRepository()
        try:
            nova_lista = Lista(
                denominacao=nome.upper(),
                tipo_id=None,
                owner_id=current_user.id,
                is_active=True
            )
            repo.add(nova_lista)
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_CREATED', f'ID: {nova_lista.id} | NAME: {nome}')
            return True, "Lista criada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao criar lista: {str(e)}"

    @staticmethod
    def update_list(lista_id: int, nome: str, current_user: Any):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            if not SimpleListService.can_write(lista, current_user):
                return False, "Sem permissão para alterar esta lista."
            lista.denominacao = nome.upper()
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_UPDATED', f'ID: {lista_id} | NEW_NAME: {nome}')
            return True, "Lista atualizada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao atualizar lista: {str(e)}"

    @staticmethod
    def delete_list(lista_id: int, current_user: Any):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            if not SimpleListService.can_manage(lista, current_user):
                return False, "Apenas o proprietário pode excluir esta lista."
            repo.delete(lista)
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_DELETED', f'ID: {lista_id}')
            return True, "Lista removida com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao remover lista: {str(e)}"

    @staticmethod
    def archive_list(lista_id: int, current_user: Any):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            if not SimpleListService.can_manage(lista, current_user):
                return False, "Apenas o proprietário pode arquivar esta lista."
            lista.is_active = False
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_ARCHIVED', f'ID: {lista_id}')
            return True, "Lista arquivada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao arquivar lista: {str(e)}"

    @staticmethod
    def reactivate_list(lista_id: int, current_user: Any):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            if not SimpleListService.can_manage(lista, current_user):
                return False, "Apenas o proprietário pode reativar esta lista."
            lista.is_active = True
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_REACTIVATED', f'ID: {lista_id}')
            return True, "Lista reativada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao reativar lista: {str(e)}"

    @staticmethod
    def share_list(lista_id: int, user_ids: List[int], current_user: Any):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            if not SimpleListService.can_manage(lista, current_user):
                return False, "Apenas o proprietário pode compartilhar esta lista."
            
            users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
            lista.shared_simple_users = [u for u in users if u.id != lista.owner_id]
            repo.commit()
            LogService.log_action(current_user.username, 'SIMPLE_LIST_SHARED', f'ID: {lista_id} | SHARED_WITH: {[u.username for u in lista.shared_simple_users]}')
            return True, "Compartilhamento atualizado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao compartilhar lista: {str(e)}"

    @staticmethod
    def create_item(lista_id: int, nome: str, link: Any = None, current_user: Any = None):
        repo_lista = ListRepository()
        lista = repo_lista.get_by_id(lista_id)
        if not lista or not SimpleListService.can_write(lista, current_user):
            return False, "Sem permissão para adicionar itens nesta lista."
        repo = ItemListaRepository()
        try:
            novo_item = ItemLista(
                lista_id=lista_id,
                item=nome.upper(),
                link=link if link else None
            )
            repo.add(novo_item)
            repo.commit()
            LogService.log_action(current_user.username if current_user else 'SYSTEM', 'SIMPLE_LIST_ITEM_CREATED', f'LIST_ID: {lista_id} | ITEM: {nome}')
            return True, "Item adicionado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao adicionar item: {str(e)}"

    @staticmethod
    def update_item(item_id: int, nome: str, link: Any = None, current_user: Any = None):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, "Item não encontrado."
            if not SimpleListService.can_write(item.lista, current_user):
                return False, "Sem permissão para editar este item."
            item.item = nome.upper()
            item.link = link if link else None
            repo.commit()
            LogService.log_action(current_user.username if current_user else 'SYSTEM', 'SIMPLE_LIST_ITEM_UPDATED', f'ID: {item_id} | ITEM: {nome}')
            return True, "Item atualizado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao atualizar item: {str(e)}"

    @staticmethod
    def delete_item(item_id: int, current_user: Any = None):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, "Item não encontrado."
            if not SimpleListService.can_write(item.lista, current_user):
                return False, "Sem permissão para remover este item."
            repo.delete(item)
            repo.commit()
            LogService.log_action(current_user.username if current_user else 'SYSTEM', 'SIMPLE_LIST_ITEM_DELETED', f'ID: {item_id}')
            return True, "Item removido com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao remover item: {str(e)}"

    @staticmethod
    def toggle_item(item_id: int, checked: Any, current_user: Any = None):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, None
            if not SimpleListService.can_write(item.lista, current_user):
                return False, None
            item.status = checked
            repo.commit()
            LogService.log_action(current_user.username if current_user else 'SYSTEM', 'SIMPLE_LIST_ITEM_TOGGLE', f'ID: {item_id} | STATUS: {checked}')
            return True, item.status
        except Exception:
            repo.rollback()
            return False, None

    @staticmethod
    def create_items_batch(lista_id: int, text: str, current_user: Any = None):
        repo_lista = ListRepository()
        lista = repo_lista.get_by_id(lista_id)
        if not lista or not SimpleListService.can_write(lista, current_user):
            return False, "Sem permissão para adicionar itens nesta lista."
        repo = ItemListaRepository()
        try:
            import re
            raw_items = re.split(r'[\n;,]', text)
            items = [i.strip().upper() for i in raw_items if i.strip()]
            
            if not items:
                return False, "Nenhum item válido encontrado."
            
            for item_name in items:
                novo_item = ItemLista(
                    lista_id=lista_id,
                    item=item_name,
                    status=False
                )
                repo.add(novo_item)
            
            repo.commit()
            LogService.log_action(current_user.username if current_user else 'SYSTEM', 'SIMPLE_LIST_BATCH_ITEMS', f'LIST_ID: {lista_id} | COUNT: {len(items)}')
            return True, f"{len(items)} itens adicionados com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao processar lote: {str(e)}"

