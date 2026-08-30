from typing import Optional, List
from sqlalchemy import or_
from app.repositories.base_repository import BaseRepository
from app.models import Tarefa, GrupoTarefas, StatusTarefas

class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Tarefa)

    def list_user_tasks(self, user_id: int, is_active: bool = True, grupo_id: Optional[int] = None) -> List[Tarefa]:
        query = self.model.query.join(Tarefa.grupo).filter(
            Tarefa.is_active == is_active,
            GrupoTarefas.is_active == is_active,
            or_(
                Tarefa.owner_id == user_id,
                Tarefa.shared_users.any(id=user_id),
                GrupoTarefas.owner_id == user_id,
                GrupoTarefas.shared_users.any(id=user_id)
            )
        )
        if grupo_id:
            query = query.filter(Tarefa.grupo_id == grupo_id)
        return query.all()


class GrupoTarefasRepository(BaseRepository):
    def __init__(self):
        super().__init__(GrupoTarefas)

    def find_by_denominacao(self, denominacao: str) -> Optional[GrupoTarefas]:
        return self.find_one_by(denominacao=denominacao)

    def list_user_groups(self, user_id: int, is_active: bool = True) -> List[GrupoTarefas]:
        return self.model.query.filter(
            GrupoTarefas.is_active == is_active,
            or_(
                GrupoTarefas.owner_id == user_id,
                GrupoTarefas.shared_users.any(id=user_id),
                GrupoTarefas.tarefas.any(
                    or_(
                        Tarefa.owner_id == user_id,
                        Tarefa.shared_users.any(id=user_id)
                    )
                )
            )
        ).order_by(GrupoTarefas.denominacao).all()

class StatusTarefasRepository(BaseRepository):
    def __init__(self):
        super().__init__(StatusTarefas)

    def find_by_denominacao(self, denominacao: str) -> Optional[StatusTarefas]:
        return self.find_one_by(denominacao=denominacao)
