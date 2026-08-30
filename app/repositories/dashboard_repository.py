from datetime import datetime
from sqlalchemy import func, or_
from typing import Dict, Any, List
from app import db
from app.models import Tarefa, GrupoTarefas, Lista, Perfume, Pessoa, Snippet, Bookmark
from app.repositories.task_repository import TaskRepository, GrupoTarefasRepository
from app.repositories.list_repository import ListRepository
from app.repositories.bookmark_repository import BookmarkRepository

class DashboardRepository:
    """
    Agrega dados para o painel principal.

    Tarefas, Grupos, Listas, Itens e Favoritos são recursos multi-tenant
    (dono + compartilhamento) e por isso são sempre consultados com escopo
    em `user_id`, reutilizando as mesmas consultas dos repositórios de cada
    módulo. Perfumes, Pessoas e Snippets são coleções compartilhadas entre
    todos os usuários por design e permanecem globais.
    """

    @staticmethod
    def get_task_stats(user_id: int) -> Dict[str, int]:
        """Total de tarefas ativas do usuário, discriminado por status."""
        tarefas = TaskRepository().list_user_tasks(user_id, is_active=True)
        stats = {"total": len(tarefas), "pendentes": 0, "iniciadas": 0, "finalizadas": 0}
        for t in tarefas:
            nome = t.status.denominacao.upper() if t.status else 'PENDENTE'
            if nome == 'INICIADO':
                stats["iniciadas"] += 1
            elif nome == 'FINALIZADO':
                stats["finalizadas"] += 1
            else:
                stats["pendentes"] += 1
        return stats

    @staticmethod
    def get_group_count(user_id: int) -> int:
        """Total de grupos de tarefas ativos visíveis ao usuário."""
        return len(GrupoTarefasRepository().list_user_groups(user_id, is_active=True))

    @staticmethod
    def get_shopping_summary(user_id: int) -> Dict[str, Any]:
        """
        Contagem de itens (comprados x pendentes) das listas de compras ativas
        do usuário, com o detalhamento de quantidade de itens por lista.
        """
        listas = ListRepository().list_user_lists(user_id, is_active=True)
        comprados = 0
        pendentes = 0
        por_lista: List[Dict[str, Any]] = []
        for lista in listas:
            n_comprados = sum(1 for item in lista.itens if item.status)
            n_total = len(lista.itens)
            comprados += n_comprados
            pendentes += (n_total - n_comprados)
            por_lista.append({
                "id": lista.id,
                "denominacao": lista.denominacao,
                "total": n_total,
                "comprados": n_comprados
            })
        por_lista.sort(key=lambda x: x["total"], reverse=True)
        return {
            "total_listas": len(listas),
            "itens_comprados": comprados,
            "itens_pendentes": pendentes,
            "itens_total": comprados + pendentes,
            "por_lista": por_lista
        }

    @staticmethod
    def get_simple_lists_count(user_id: int) -> int:
        """Total de listas simples (checklists) ativas visíveis ao usuário."""
        return len(ListRepository().list_user_simple_lists(user_id, is_active=True))

    @staticmethod
    def get_bookmarks_count(user_id: int) -> int:
        """Total de favoritos ativos visíveis ao usuário (próprios + compartilhados)."""
        return len(BookmarkRepository().list_user_bookmarks(user_id, is_active=True))

    @staticmethod
    def get_catalog_counts() -> Dict[str, int]:
        """Totais das coleções compartilhadas entre todos os usuários."""
        return {
            "perfumes_count": db.session.query(func.count(Perfume.id)).scalar() or 0,
            "pessoas_count": db.session.query(func.count(Pessoa.id)).scalar() or 0,
            "snippets_count": db.session.query(func.count(Snippet.id)).scalar() or 0,
        }

    @staticmethod
    def get_completed_tasks_stats(user_id: int, since_datetime: datetime) -> List[Any]:
        """Contagem diária de tarefas concluídas pelo usuário nos últimos N dias."""
        return db.session.query(
            func.date(Tarefa.data_executado).label('date'),
            func.count(Tarefa.id).label('count')
        ).join(Tarefa.grupo).filter(
            Tarefa.data_executado >= since_datetime,
            or_(
                Tarefa.owner_id == user_id,
                Tarefa.shared_users.any(id=user_id),
                GrupoTarefas.owner_id == user_id,
                GrupoTarefas.shared_users.any(id=user_id)
            )
        ).group_by(
            func.date(Tarefa.data_executado)
        ).all()

    # --- Compartilhados comigo -------------------------------------------------

    @staticmethod
    def get_shared_tasks(user_id: int) -> List[Tarefa]:
        return Tarefa.query.join(Tarefa.grupo).filter(
            Tarefa.is_active.is_(True),
            GrupoTarefas.is_active.is_(True),
            Tarefa.shared_users.any(id=user_id)
        ).all()

    @staticmethod
    def get_shared_groups(user_id: int) -> List[GrupoTarefas]:
        return GrupoTarefas.query.filter(
            GrupoTarefas.is_active.is_(True),
            GrupoTarefas.shared_users.any(id=user_id)
        ).all()

    @staticmethod
    def get_shared_lists(user_id: int) -> List[Lista]:
        return Lista.query.filter(
            Lista.is_active.is_(True),
            Lista.tipo_id.is_not(None),
            Lista.shared_users.any(id=user_id)
        ).all()

    @staticmethod
    def get_shared_simple_lists(user_id: int) -> List[Lista]:
        return Lista.query.filter(
            Lista.is_active.is_(True),
            Lista.tipo_id.is_(None),
            Lista.shared_simple_users.any(id=user_id)
        ).all()

    @staticmethod
    def get_shared_bookmarks(user_id: int) -> List[Bookmark]:
        return Bookmark.query.filter(
            Bookmark.is_active.is_(True),
            Bookmark.shared_users.any(id=user_id)
        ).all()
