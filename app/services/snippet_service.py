from app.repositories.base_repository import BaseRepository
from app.models import Snippet
from app.services.log_service import LogService

class SnippetService:
    @staticmethod
    def get_snippet_by_id(id):
        repo = BaseRepository(Snippet)
        return repo.get_or_404(id)

    @staticmethod
    def get_all_snippets(search=None):

        repo = BaseRepository(Snippet)
        if search:
            return Snippet.query.filter(
                (Snippet.titulo.ilike(f'%{search}%')) | 
                (Snippet.conteudo.ilike(f'%{search}%')) |
                (Snippet.linguagem.ilike(f'%{search}%'))
            ).all()
        return repo.list_all(order_by=Snippet.data_criacao.desc())

    @staticmethod
    def create_snippet(form_data, current_user):
        repo = BaseRepository(Snippet)
        titulo = form_data.get('titulo')
        conteudo = form_data.get('conteudo')
        linguagem = form_data.get('linguagem', 'plaintext')
        
        if titulo and conteudo:
            snippet = Snippet(titulo=titulo, conteudo=conteudo, linguagem=linguagem)
            repo.add(snippet)
            repo.commit()
            LogService.log_action(current_user.username, 'SNIPPET_CREATED', f'ID: {snippet.id} | TITLE: {titulo}')
            return snippet
        return None

    @staticmethod
    def update_snippet(id, form_data, current_user):
        repo = BaseRepository(Snippet)
        snippet = repo.get_or_404(id)
        titulo = form_data.get('titulo')
        conteudo = form_data.get('conteudo')
        linguagem = form_data.get('linguagem', 'plaintext')
        
        if titulo and conteudo:
            snippet.titulo = titulo
            snippet.conteudo = conteudo
            snippet.linguagem = linguagem
            repo.commit()
            LogService.log_action(current_user.username, 'SNIPPET_UPDATED', f'ID: {id} | TITLE: {titulo}')
            return snippet
        return None

    @staticmethod
    def delete_snippet(id, current_user):
        repo = BaseRepository(Snippet)
        snippet = repo.get_or_404(id)
        titulo = snippet.titulo
        repo.delete(snippet)
        repo.commit()
        LogService.log_action(current_user.username, 'SNIPPET_DELETED', f'ID: {id}')
        return titulo
