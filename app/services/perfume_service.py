from app.repositories.base_repository import BaseRepository
from app.models import Perfume
from app.services.log_service import LogService

class PerfumeService:
    @staticmethod
    def get_all_perfumes():
        repo = BaseRepository(Perfume)
        return repo.list_all(order_by=Perfume.nome)

    @staticmethod
    def create_perfume(form_data, current_user):
        repo = BaseRepository(Perfume)
        try:
            valor = form_data.get('valor')
            novo_perfume = Perfume(
                nome=form_data.get('nome'),
                marca=form_data.get('marca'),
                correspondente=form_data.get('correspondente'),
                valor=float(valor) if valor else None,
                url=form_data.get('url'),
                url_imagem=form_data.get('url_imagem')
            )
            repo.add(novo_perfume)
            repo.commit()
            LogService.log_action(current_user.username, 'PERFUME_CREATED', f'ID: {novo_perfume.id} | NOME: {novo_perfume.nome}')
            return novo_perfume
        except Exception as e:
            raise e

    @staticmethod
    def update_perfume(id, form_data, current_user):
        repo = BaseRepository(Perfume)
        perfume = repo.get_or_404(id)
        try:
            valor = form_data.get('valor')
            perfume.nome = form_data.get('nome')
            perfume.marca = form_data.get('marca')
            perfume.correspondente = form_data.get('correspondente')
            perfume.valor = float(valor) if valor else None
            perfume.url = form_data.get('url')
            perfume.url_imagem = form_data.get('url_imagem')
            repo.commit()
            LogService.log_action(current_user.username, 'PERFUME_UPDATED', f'ID: {id} | NOME: {perfume.nome}')
            return perfume
        except Exception as e:
            raise e

    @staticmethod
    def delete_perfume(id, current_user):
        repo = BaseRepository(Perfume)
        perfume = repo.get_or_404(id)
        nome = perfume.nome
        repo.delete(perfume)
        repo.commit()
        LogService.log_action(current_user.username, 'PERFUME_DELETED', f'ID: {id} | NOME: {nome}')
        return nome
