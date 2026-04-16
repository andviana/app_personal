from app.repositories.base_repository import BaseRepository
from app.models import Snippet, Tag, SnippetTag
from app.services.log_service import LogService
from app import db

class SnippetService:
    @staticmethod
    def get_snippet_by_id(id):
        repo = BaseRepository(Snippet)
        return repo.get_or_404(id)

    @staticmethod
    def get_snippet_by_uuid(uuid_str):
        repo = BaseRepository(Snippet)
        return repo.find_one_or_404(uuid=uuid_str)

    @staticmethod
    def get_all_snippets(search=None):
        if search:
            # Filtro por TAG (Ex: #PYTHON)
            if search.startswith('#'):
                tag_name = search[1:].upper()
                return Snippet.query.join(Snippet.tags).filter(Tag.denominacao == tag_name).all()
            
            # Filtro por TEXTO
            return Snippet.query.filter(
                (Snippet.titulo.ilike(f'%{search}%')) | 
                (Snippet.conteudo.ilike(f'%{search}%')) |
                (Snippet.descricao.ilike(f'%{search}%'))
            ).all()
        
        return Snippet.query.order_by(Snippet.data_criacao.desc()).all()

    @staticmethod
    def create_snippet(form_data, current_user):
        repo = BaseRepository(Snippet)
        titulo = form_data.get('titulo')
        conteudo = form_data.get('conteudo')
        descricao = form_data.get('descricao')
        if titulo and conteudo:
            snippet = Snippet(titulo=titulo, conteudo=conteudo, descricao=descricao)
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
        descricao = form_data.get('descricao')
        if titulo and conteudo:
            snippet.titulo = titulo
            snippet.conteudo = conteudo
            snippet.descricao = descricao
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

    # --- Métodos de Tags ---

    @staticmethod
    def get_all_tags():
        """Retorna todas as tags cadastradas."""
        return Tag.query.order_by(Tag.denominacao).all()

    @staticmethod
    def create_tag(denominacao, cor, current_user):
        """Cria uma nova tag (Garante UPPERCASE)."""
        if not denominacao: return None
        
        tag_nome = denominacao.upper()
        # Verificar se já existe
        exists = Tag.query.filter_by(denominacao=tag_nome).first()
        if exists: return exists
        
        nova_tag = Tag(denominacao=tag_nome, cor=cor)
        db.session.add(nova_tag)
        db.session.commit()
        LogService.log_action(current_user.username, 'TAG_CREATED', f'NAME: {tag_nome}')
        return nova_tag

    @staticmethod
    def delete_tag(tag_id, current_user):
        """Exclui uma tag e remove associações."""
        tag = Tag.query.get_or_404(tag_id)
        # SQLAlchemy handles many-to-many deletion if configured, 
        # but let's be explicit and delete SnipetTag entries first if needed.
        SnippetTag.query.filter_by(tag_id=tag_id).delete()
        
        db.session.delete(tag)
        db.session.commit()
        LogService.log_action(current_user.username, 'TAG_DELETED', f'ID: {tag_id}')
        return True

    @staticmethod
    def toggle_snippet_tag(snippet_id, tag_id, current_user):
        """Associa ou desassocia uma tag de um snippet."""
        snippet = Snippet.query.get_or_404(snippet_id)
        tag = Tag.query.get_or_404(tag_id)
        
        if tag in snippet.tags:
            snippet.tags.remove(tag)
            action = 'TAG_REMOVED'
        else:
            snippet.tags.append(tag)
            action = 'TAG_ADDED'
            
        db.session.commit()
        LogService.log_action(current_user.username, action, f'SNIPPET: {snippet_id} | TAG: {tag.denominacao}')
        return True
