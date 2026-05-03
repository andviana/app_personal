from app import db
from app.models import Lista, ItemLista
from app.repositories.base_repository import BaseRepository

class SimpleListService:
    @staticmethod
    def get_all_lists():
        return Lista.query.filter(Lista.tipo_id == None).order_by(Lista.denominacao).all()

    @staticmethod
    def get_list_by_id(lista_id):
        return Lista.query.get(lista_id)

    @staticmethod
    def create_list(nome):
        try:
            repo = BaseRepository(Lista)
            nova_lista = Lista(denominacao=nome.upper())
            repo.add(nova_lista)
            repo.commit()
            return True, "Lista criada com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao criar lista: {str(e)}"

    @staticmethod
    def update_list(lista_id, nome):
        try:
            lista = Lista.query.get(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            lista.denominacao = nome.upper()
            db.session.commit()
            return True, "Lista atualizada com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar lista: {str(e)}"

    @staticmethod
    def delete_list(lista_id):
        try:
            lista = Lista.query.get(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            db.session.delete(lista)
            db.session.commit()
            return True, "Lista removida com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao remover lista: {str(e)}"

    @staticmethod
    def create_item(lista_id, nome, link=None):
        try:
            novo_item = ItemLista(
                lista_id=lista_id,
                item=nome.upper(),
                link=link
            )
            db.session.add(novo_item)
            db.session.commit()
            return True, "Item adicionado com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao adicionar item: {str(e)}"

    @staticmethod
    def update_item(item_id, nome, link=None):
        try:
            item = ItemLista.query.get(item_id)
            if not item:
                return False, "Item não encontrado."
            item.item = nome.upper()
            item.link = link
            db.session.commit()
            return True, "Item atualizado com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao atualizar item: {str(e)}"

    @staticmethod
    def delete_item(item_id):
        try:
            item = ItemLista.query.get(item_id)
            if not item:
                return False, "Item não encontrado."
            db.session.delete(item)
            db.session.commit()
            return True, "Item removido com sucesso!"
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao remover item: {str(e)}"

    @staticmethod
    def toggle_item(item_id, checked):
        try:
            item = ItemLista.query.get(item_id)
            if not item:
                return False, None
            item.status = checked
            db.session.commit()
            return True, item.status
        except Exception:
            db.session.rollback()
            return False, None
