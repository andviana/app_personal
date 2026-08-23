from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models import Tarefa, GrupoTarefas, StatusTarefas

class TaskRepository(BaseRepository):
    def __init__(self):
        super().__init__(Tarefa)

class GrupoTarefasRepository(BaseRepository):
    def __init__(self):
        super().__init__(GrupoTarefas)

    def find_by_denominacao(self, denominacao: str) -> Optional[GrupoTarefas]:
        return self.find_one_by(denominacao=denominacao)

class StatusTarefasRepository(BaseRepository):
    def __init__(self):
        super().__init__(StatusTarefas)

    def find_by_denominacao(self, denominacao: str) -> Optional[StatusTarefas]:
        return self.find_one_by(denominacao=denominacao)
