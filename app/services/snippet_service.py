from app.repositories.snippet_repository import SnippetRepository, TagRepository, SnippetTagRepository
from app.models import Snippet, Tag, SnippetTag
from app.services.log_service import LogService

class SnippetService:
    @staticmethod
    def get_snippet_by_id(id):
        repo = SnippetRepository()
        return repo.get_or_404(id)

    @staticmethod
    def get_snippet_by_uuid(uuid_str):
        repo = SnippetRepository()
        return repo.find_one_or_404(uuid=uuid_str)

    @staticmethod
    def get_all_snippets(search=None):
        repo = SnippetRepository()
        return repo.search_snippets(search)

    @staticmethod
    def create_snippet(form_data, current_user):
        repo = SnippetRepository()
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
        repo = SnippetRepository()
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
        repo = SnippetRepository()
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
        repo = TagRepository()
        return repo.list_ordered_by_denominacao()

    @staticmethod
    def create_tag(denominacao, cor, current_user):
        """Cria uma nova tag (Garante UPPERCASE)."""
        if not denominacao: return None
        
        tag_nome = denominacao.upper()
        repo = TagRepository()
        # Verificar se já existe
        exists = repo.find_by_denominacao(tag_nome)
        if exists: return exists
        
        nova_tag = Tag(denominacao=tag_nome, cor=cor)
        repo.add(nova_tag)
        repo.commit()
        LogService.log_action(current_user.username, 'TAG_CREATED', f'NAME: {tag_nome}')
        return nova_tag

    @staticmethod
    def delete_tag(tag_id, current_user):
        """Exclui uma tag e remove associações."""
        repo = TagRepository()
        repo_st = SnippetTagRepository()
        
        tag = repo.get_or_404(tag_id)
        # SQLAlchemy handles many-to-many deletion if configured, 
        # but let's be explicit and delete SnippetTag entries first if needed.
        repo_st.delete_by_tag_id(tag_id)
        
        repo.delete(tag)
        repo.commit()
        LogService.log_action(current_user.username, 'TAG_DELETED', f'ID: {tag_id}')
        return True

    @staticmethod
    def toggle_snippet_tag(snippet_id, tag_id, current_user):
        """Associa ou desassocia uma tag de um snippet."""
        repo = SnippetRepository()
        repo_tag = TagRepository()
        
        snippet = repo.get_or_404(snippet_id)
        tag = repo_tag.get_or_404(tag_id)
        
        if tag in snippet.tags:
            snippet.tags.remove(tag)
            action = 'TAG_REMOVED'
        else:
            snippet.tags.append(tag)
            action = 'TAG_ADDED'
            
        repo.commit()
        LogService.log_action(current_user.username, action, f'SNIPPET: {snippet_id} | TAG: {tag.denominacao}')
        return True
