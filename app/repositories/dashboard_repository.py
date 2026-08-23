from datetime import datetime
from sqlalchemy import func
from typing import Dict, Any, List
from app import db
from app.models import Tarefa, ItemLista, Lista, Perfume, Pessoa, Snippet

class DashboardRepository:
    @staticmethod
    def get_dashboard_counts() -> Dict[str, int]:
        return {
            "tarefas_pendentes": db.session.query(func.count(Tarefa.id)).filter(Tarefa.data_executado == None).scalar() or 0,
            "listas_ativas": db.session.query(func.count(Lista.id)).scalar() or 0,
            "perfumes_count": db.session.query(func.count(Perfume.id)).scalar() or 0,
            "pessoas_count": db.session.query(func.count(Pessoa.id)).scalar() or 0,
            "snippets_count": db.session.query(func.count(Snippet.id)).scalar() or 0,
            "itens_count": db.session.query(func.count(ItemLista.id)).scalar() or 0
        }

    @staticmethod
    def get_completed_tasks_stats(since_datetime: datetime) -> List[Any]:
        return db.session.query(
            func.date(Tarefa.data_executado).label('date'),
            func.count(Tarefa.id).label('count')
        ).filter(
            Tarefa.data_executado >= since_datetime
        ).group_by(
            func.date(Tarefa.data_executado)
        ).all()

    @staticmethod
    def get_shopping_metrics() -> Dict[str, float]:
        total_estimated = db.session.query(func.sum(ItemLista.valor)).scalar() or 0.0
        total_purchased = db.session.query(
            func.sum(ItemLista.valor)
        ).filter(
            ItemLista.status == True
        ).scalar() or 0.0
        
        return {
            "total_estimated": float(total_estimated),
            "total_purchased": float(total_purchased)
        }
