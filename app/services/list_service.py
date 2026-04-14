from app.repositories.base_repository import BaseRepository
from app.models import Lista, ItemLista, TipoLista, GrupoItem
from app.services.log_service import LogService

class ListService:
    @staticmethod
    def get_lists_data():
        repo_listas = BaseRepository(Lista)
        repo_tipos = BaseRepository(TipoLista)
        return repo_listas.list_all(order_by=Lista.denominacao), repo_tipos.list_all(order_by=TipoLista.denominacao)

    @staticmethod
    def create_list(denominacao, tipo_id, current_user):
        if denominacao:
            repo = BaseRepository(Lista)
            nova_lista = Lista(denominacao=denominacao, tipo_id=tipo_id)
            repo.add(nova_lista)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_CREATED', f'ID: {nova_lista.id} | TITLE: {denominacao}')
            return nova_lista
        return None

    @staticmethod
    def delete_list(id, current_user):
        repo = BaseRepository(Lista)
        lista = repo.get_or_404(id)
        denominacao = lista.denominacao
        repo.delete(lista)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_DELETED', f'ID: {id} | TITLE: {denominacao}')
        return denominacao

    @staticmethod
    def get_list_detail(id):
        repo_lista = BaseRepository(Lista)
        repo_grupos = BaseRepository(GrupoItem)
        lista = repo_lista.get_or_404(id)
        grupos = repo_grupos.list_all(order_by=GrupoItem.denominacao)
        return lista, grupos

    @staticmethod
    def create_list_item(lista_id, item_text, grupo_id, valor, link, current_user):
        if item_text:
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
                item=item_text,
                grupo_id=grupo_id,
                valor=valor,
                link=link
            )
            repo.add(novo_item)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_ITEM_CREATED', f'LIST_ID: {lista_id} | ITEM: {item_text}')
            return novo_item
        return None

    @staticmethod
    def update_list_item(item_id, item_text, grupo_id, valor, link, current_user):
        repo = BaseRepository(ItemLista)
        item = repo.get_or_404(item_id)
        if item_text:
            item.item = item_text
            item.grupo_id = grupo_id if grupo_id else None
            item.valor = valor if valor else None
            item.link = link if link else None
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_ITEM_UPDATED', f'ID: {item_id} | ITEM: {item_text}')
            return item
        return None

    @staticmethod
    def toggle_item_check(item_id, checked, current_user):
        repo = BaseRepository(ItemLista)
        item = repo.get_or_404(item_id)
        if checked is None:
            item.status = not item.status
        else:
            item.status = checked
        repo.commit()
        log_status = "COMPRADO" if item.status else "PENDENTE"
        LogService.log_action(current_user.username, 'LIST_ITEM_TOGGLE', f'ID: {item_id} | NEW_STATUS: {log_status}')
        return item

    @staticmethod
    def delete_item(item_id, current_user):
        repo = BaseRepository(ItemLista)
        item = repo.get_or_404(item_id)
        item_text = item.item
        repo.delete(item)
        repo.commit()
        LogService.log_action(current_user.username, 'LIST_ITEM_DELETED', f'ID: {item_id}')
        return item_text

    @staticmethod
    def create_list_type(denominacao, current_user):
        if denominacao:
            repo = BaseRepository(TipoLista)
            novo_tipo = TipoLista(denominacao=denominacao)
            repo.add(novo_tipo)
            repo.commit()
            LogService.log_action(current_user.username, 'LIST_TYPE_CREATED', f'NAME: {denominacao}')
            return novo_tipo
        return None

    @staticmethod
    def create_item_group(denominacao, current_user):
        if denominacao:
            repo = BaseRepository(GrupoItem)
            novo_grupo = GrupoItem(denominacao=denominacao)
            repo.add(novo_grupo)
            repo.commit()
            LogService.log_action(current_user.username, 'ITEM_GROUP_CREATED', f'NAME: {denominacao}')
            return novo_grupo
        return None
