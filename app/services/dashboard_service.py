from datetime import datetime, timedelta, timezone, date as py_date
from sqlalchemy import func, select
from typing import Dict, Any, List
from app import db
from app.models import Tarefa, ItemLista, Lista, Perfume, Pessoa, Snippet

class DashboardService:
    @staticmethod
    def get_dashboard_counts() -> Dict[str, int]:
        """Aggregates totals for all main entities."""
        return {
            "tarefas_pendentes": db.session.query(func.count(Tarefa.id)).filter(Tarefa.data_executado == None).scalar() or 0,
            "listas_ativas": db.session.query(func.count(Lista.id)).scalar() or 0,
            "perfumes_count": db.session.query(func.count(Perfume.id)).scalar() or 0,
            "pessoas_count": db.session.query(func.count(Pessoa.id)).scalar() or 0,
            "snippets_count": db.session.query(func.count(Snippet.id)).scalar() or 0,
            "itens_count": db.session.query(func.count(ItemLista.id)).scalar() or 0
        }

    @staticmethod
    def get_contribution_stats() -> Dict[str, int]:
        """
        Calculates completion counts per day for the last 365 days.
        Returns a dict: { "YYYY-MM-DD": count }
        """
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        
        # Query tasks completed in the last year
        results = db.session.query(
            func.date(Tarefa.data_executado).label('date'),
            func.count(Tarefa.id).label('count')
        ).filter(
            Tarefa.data_executado >= one_year_ago
        ).group_by(
            func.date(Tarefa.data_executado)
        ).all()
        
        return {str(r.date): r.count for r in results if r.date}

    @staticmethod
    def get_shopping_metrics() -> Dict[str, float]:
        """
        Calculates financial metrics for shopping lists.
        """
        # Estimated: Sum of all item values
        total_estimated = db.session.query(func.sum(ItemLista.valor)).scalar() or 0.0
        
        # Purchased: Sum of values for items where status is True
        total_purchased = db.session.query(
            func.sum(ItemLista.valor)
        ).filter(
            ItemLista.status == True
        ).scalar() or 0.0
        
        return {
            "total_estimated": float(total_estimated),
            "total_purchased": float(total_purchased)
        }

    @staticmethod
    def get_dashboard_data() -> Dict[str, Any]:
        """Aggregates all data needed for the dashboard."""
        counts = DashboardService.get_dashboard_counts()
        contributions = DashboardService.get_contribution_stats()
        shopping = DashboardService.get_shopping_metrics()
        
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
            **counts,
            "contribution_data": contributions,
            "shopping_metrics": shopping,
            "contribution_calendar": contribution_calendar,
            "month_labels": month_labels
        }

