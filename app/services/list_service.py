from app.repositories.base_repository import BaseRepository
from app.models import Lista, ItemLista, TipoLista, GrupoItem
from app.services.log_service import LogService

class ListService:
    @staticmethod
    def get_lists_data():
        repo_listas = BaseRepository(Lista)
        repo_tipos = BaseRepository(TipoLista)
        return repo_listas.list_all(order_by=Lista.titulo), repo_tipos.list_all(order_by=TipoLista.denominacao)

    @staticmethod
    def create_list(titulo, tipo_id, current_user):
        if titulo:
            repo = BaseRepository(Lista)
            nova_lista = Lista(titulo=titulo, tipo_id=tipo_id)
            repo.add(nova_lista)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_CREATED', f'ID: {nova_lista.id} | TITLE: {titulo}')
            return nova_lista
        return None

    @staticmethod
    def delete_list(id, current_user):
        repo = BaseRepository(Lista)
        lista = repo.get_or_404(id)
        titulo = lista.titulo
        repo.delete(lista)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_DELETED', f'ID: {id} | TITLE: {titulo}')
        return titulo

    @staticmethod
    def get_list_detail(id):
        repo_lista = BaseRepository(Lista)
        repo_grupos = BaseRepository(GrupoItem)
        lista = repo_lista.get_or_404(id)
        grupos = repo_grupos.list_all(order_by=GrupoItem.denominacao)
        return lista, grupos

    @staticmethod
    def create_list_item(lista_id, descricao, grupo_id, valor, url, current_user):
        if descricao:
            repo = BaseRepository(ItemLista)
            # Garantir grupo 'OUTROS' se não informado
            if not grupo_id:
                repo_g = BaseRepository(GrupoItem)
                outros = GrupoItem.query.filter_by(denominacao='OUTROS').first()
                if not outros:
                    outros = GrupoItem(denominacao='OUTROS')
                    repo_g.add(outros)
                    repo_g.commit()
                grupo_id = outros.id
            
            novo_item = ItemLista(
                lista_id=lista_id,
                descricao=descricao,
                grupo_id=grupo_id,
                valor=valor,
                url=url
            )
            repo.add(novo_item)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_ITEM_CREATED', f'LIST_ID: {lista_id} | DESC: {descricao}')
            return novo_item
        return None

    @staticmethod
    def toggle_item_check(item_id, checked, current_user):
        repo = BaseRepository(ItemLista)
        item = repo.get_or_404(item_id)
        item.comprado = checked
        repo.commit()
        status = "COMPRADO" if checked else "PENDENTE"
        LogService.log_action(current_user.username, 'LIST_ITEM_TOGGLE', f'ID: {item_id} | NEW_STATUS: {status}')
        return item

    @staticmethod
    def delete_item(item_id, current_user):
        repo = BaseRepository(ItemLista)
        item = repo.get_or_404(item_id)
        desc = item.descricao
        repo.delete(item)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_ITEM_DELETED', f'ID: {item_id}')
        return desc
