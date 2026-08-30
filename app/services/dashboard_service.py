from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from flask import url_for
from app.repositories.dashboard_repository import DashboardRepository

class DashboardService:
    @staticmethod
    def get_contribution_stats(current_user: Any) -> Dict[str, int]:
        """
        Calculates completion counts per day for the last 365 days, scoped to the current user.
        Returns a dict: { "YYYY-MM-DD": count }
        """
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        results = DashboardRepository.get_completed_tasks_stats(current_user.id, one_year_ago)
        return {str(r.date): r.count for r in results if r.date}

    @staticmethod
    def get_shared_with_me(current_user: Any) -> List[Dict[str, Any]]:
        """Agrega tudo o que foi compartilhado com o usuário atual (tarefas, grupos, listas e favoritos)."""
        user_id = current_user.id
        items: List[Dict[str, Any]] = []

        for t in DashboardRepository.get_shared_tasks(user_id):
            items.append({
                "tipo": "Tarefa", "icon": "ph-check-square", "cor": "success",
                "titulo": t.descricao,
                "owner": t.owner.username if t.owner else "—",
                "url": url_for('tasks.index', grupo_id=t.grupo_id)
            })
        for g in DashboardRepository.get_shared_groups(user_id):
            items.append({
                "tipo": "Grupo de Tarefas", "icon": "ph-folder-open", "cor": "success",
                "titulo": g.denominacao,
                "owner": g.owner.username if g.owner else "—",
                "url": url_for('tasks.index', grupo_id=g.id)
            })
        for l in DashboardRepository.get_shared_lists(user_id):
            items.append({
                "tipo": "Lista de Compras", "icon": "ph-shopping-bag", "cor": "primary",
                "titulo": l.denominacao,
                "owner": l.owner.username if l.owner else "—",
                "url": url_for('lists.detail', id=l.id)
            })
        for l in DashboardRepository.get_shared_simple_lists(user_id):
            items.append({
                "tipo": "Lista Simples", "icon": "ph-list-bullets", "cor": "primary",
                "titulo": l.denominacao,
                "owner": l.owner.username if l.owner else "—",
                "url": url_for('simple_lists.detail', id=l.id)
            })
        for b in DashboardRepository.get_shared_bookmarks(user_id):
            items.append({
                "tipo": "Favorito", "icon": "ph-bookmark-simple", "cor": "warning",
                "titulo": b.titulo,
                "owner": b.owner.username if b.owner else "—",
                "url": url_for('bookmarks.index')
            })
        return items

    @staticmethod
    def get_dashboard_data(current_user: Any) -> Dict[str, Any]:
        """Aggregates all data needed for the dashboard, scoped to the current user."""
        tasks = DashboardRepository.get_task_stats(current_user.id)
        grupos_count = DashboardRepository.get_group_count(current_user.id)
        shopping = DashboardRepository.get_shopping_summary(current_user.id)
        listas_simples_count = DashboardRepository.get_simple_lists_count(current_user.id)
        bookmarks_count = DashboardRepository.get_bookmarks_count(current_user.id)
        catalog = DashboardRepository.get_catalog_counts()
        contributions = DashboardService.get_contribution_stats(current_user)
        shared_with_me = DashboardService.get_shared_with_me(current_user)

        # Calculate start date (Monday of the week 52 weeks ago)
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=363)
        start_date -= timedelta(days=start_date.weekday())

        contribution_calendar: List[Dict[str, Any]] = []
        month_labels: List[Dict[str, Any]] = []
        months_br = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        current_month = -1

        for col in range(52):
            col_start_date = start_date + timedelta(days=col * 7)
            if col_start_date.month != current_month:
                current_month = col_start_date.month
                if not month_labels or (col - month_labels[-1]["col"] >= 3):
                    month_labels.append({
                        "name": months_br[current_month - 1],
                        "col": col
                    })

            for day in range(7):
                curr_date = start_date + timedelta(days=col * 7 + day)
                count = contributions.get(curr_date.isoformat(), 0)

                contribution_calendar.append({
                    "count": count,
                    "date": curr_date.strftime('%d/%b'),
                    "day_name": curr_date.strftime('%A')
                })

        return {
            "tasks": tasks,
            "grupos_count": grupos_count,
            "shopping": shopping,
            "listas_simples_count": listas_simples_count,
            "bookmarks_count": bookmarks_count,
            **catalog,
            "shared_with_me": shared_with_me,
            "contribution_data": contributions,
            "contribution_calendar": contribution_calendar,
            "month_labels": month_labels
        }
