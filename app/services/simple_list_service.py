from app.repositories.list_repository import ListRepository, ItemListaRepository
from app.models import Lista, ItemLista

class SimpleListService:
    @staticmethod
    def get_all_lists():
        repo = ListRepository()
        return repo.list_simple_lists()

    @staticmethod
    def get_list_by_id(lista_id):
        repo = ListRepository()
        lista = repo.get_by_id(lista_id)
        if lista:
            lista.itens.sort(key=lambda x: (x.status, x.item))
        return lista

    @staticmethod
    def create_list(nome):
        repo = ListRepository()
        try:
            nova_lista = Lista(denominacao=nome.upper())
            repo.add(nova_lista)
            repo.commit()
            return True, "Lista criada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao criar lista: {str(e)}"

    @staticmethod
    def update_list(lista_id, nome):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            lista.denominacao = nome.upper()
            repo.commit()
            return True, "Lista atualizada com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao atualizar lista: {str(e)}"

    @staticmethod
    def delete_list(lista_id):
        repo = ListRepository()
        try:
            lista = repo.get_by_id(lista_id)
            if not lista:
                return False, "Lista não encontrada."
            repo.delete(lista)
            repo.commit()
            return True, "Lista removida com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao remover lista: {str(e)}"

    @staticmethod
    def create_item(lista_id, nome, link=None):
        repo = ItemListaRepository()
        try:
            novo_item = ItemLista(
                lista_id=lista_id,
                item=nome.upper(),
                link=link if link else None
            )
            repo.add(novo_item)
            repo.commit()
            return True, "Item adicionado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao adicionar item: {str(e)}"

    @staticmethod
    def update_item(item_id, nome, link=None):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, "Item não encontrado."
            item.item = nome.upper()
            item.link = link if link else None
            repo.commit()
            return True, "Item atualizado com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao atualizar item: {str(e)}"

    @staticmethod
    def delete_item(item_id):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, "Item não encontrado."
            repo.delete(item)
            repo.commit()
            return True, "Item removido com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao remover item: {str(e)}"

    @staticmethod
    def toggle_item(item_id, checked):
        repo = ItemListaRepository()
        try:
            item = repo.get_by_id(item_id)
            if not item:
                return False, None
            item.status = checked
            repo.commit()
            return True, item.status
        except Exception:
            repo.rollback()
            return False, None

    @staticmethod
    def create_items_batch(lista_id, text):
        repo = ItemListaRepository()
        try:
            import re
            # Divide por enter, ponto e vírgula ou vírgula
            raw_items = re.split(r'[\n;,]', text)
            
            # Limpa espaços e remove itens vazios
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
            return True, f"{len(items)} itens adicionados com sucesso!"
        except Exception as e:
            repo.rollback()
            return False, f"Erro ao processar lote: {str(e)}"
