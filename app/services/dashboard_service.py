from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from app.repositories.dashboard_repository import DashboardRepository

class DashboardService:
    @staticmethod
    def get_dashboard_counts() -> Dict[str, int]:
        """Aggregates totals for all main entities."""
        return DashboardRepository.get_dashboard_counts()

    @staticmethod
    def get_contribution_stats() -> Dict[str, int]:
        """
        Calculates completion counts per day for the last 365 days.
        Returns a dict: { "YYYY-MM-DD": count }
        """
        one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
        results = DashboardRepository.get_completed_tasks_stats(one_year_ago)
        return {str(r.date): r.count for r in results if r.date}

    @staticmethod
    def get_shopping_metrics() -> Dict[str, float]:
        """
        Calculates financial metrics for shopping lists.
        """
        return DashboardRepository.get_shopping_metrics()

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
