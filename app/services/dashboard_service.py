from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from app import db
from app.models import Tarefa, ItemLista, Lista, Perfume, Pessoa, Snippet

class DashboardService:
    @staticmethod
    def get_dashboard_counts():
        """Aggregates totals for all main entities."""
        return {
            "tarefas_pendentes": Tarefa.query.filter_by(data_executado=None).count(),
            "listas_ativas": Lista.query.count(),
            "perfumes_count": Perfume.query.count(),
            "pessoas_count": Pessoa.query.count(),
            "snippets_count": Snippet.query.count(),
            "itens_count": ItemLista.query.count()
        }

    @staticmethod
    def get_contribution_stats():
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
    def get_shopping_metrics():
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
            "total_estimated": total_estimated,
            "total_purchased": total_purchased
        }

    @staticmethod
    def get_dashboard_data():
        """Aggregates all data needed for the dashboard."""
        counts = DashboardService.get_dashboard_counts()
        contributions = DashboardService.get_contribution_stats()
        shopping = DashboardService.get_shopping_metrics()
        
        # Calculate start date (Monday of the week 52 weeks ago)
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=363) # Start 364 days ago
        start_date -= timedelta(days=start_date.weekday()) # Align to Monday
        
        # We want 26 bi-weeks (364 days total)
        biweekly_calendar = []
        month_labels = []
        months_br = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        current_month = -1

        for col in range(26):
            # Check for month change at the start of each bi-week column
            col_start_date = start_date + timedelta(days=col * 14)
            if col_start_date.month != current_month:
                current_month = col_start_date.month
                if not month_labels or (col - month_labels[-1]["col"] > 1):
                    month_labels.append({
                        "name": months_br[current_month - 1],
                        "col": col
                    })

            # 7 rows per column (Mon-Sun)
            for day in range(7):
                d1 = start_date + timedelta(days=col * 14 + day)
                d2 = start_date + timedelta(days=col * 14 + day + 7)
                
                c1 = contributions.get(d1.isoformat(), 0)
                c2 = contributions.get(d2.isoformat(), 0)
                
                biweekly_calendar.append({
                    "count": c1 + c2,
                    "range": f"{d1.strftime('%d/%b')} a {d2.strftime('%d/%b')}"
                })
        
        return {
            **counts,
            "contribution_data": contributions,
            "shopping_metrics": shopping,
            "biweekly_calendar": biweekly_calendar,
            "month_labels": month_labels
        }
