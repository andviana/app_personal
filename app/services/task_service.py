from datetime import datetime, timezone
from typing import List, Optional, Any
from sqlalchemy.orm import joinedload
from app.repositories.base_repository import BaseRepository
from app.models import Tarefa, GrupoTarefas
from app.services.log_service import LogService
from app.services.seed_service import SeedService

class TaskService:
    @staticmethod
    def get_tasks_data() -> List[GrupoTarefas]:
        """Fetches all groups with their tasks eagerly loaded to prevent N+1 queries."""
        SeedService.init_tasks_defaults()
        repo_grupos = BaseRepository(GrupoTarefas)
        return repo_grupos.list_all(
            order_by=GrupoTarefas.denominacao,
            options=[joinedload(GrupoTarefas.tarefas)]
        )

    @staticmethod
    def get_all_groups() -> List[GrupoTarefas]:
        """Fetches all groups with task counts."""
        SeedService.init_tasks_defaults()
        repo_grupos = BaseRepository(GrupoTarefas)
        return repo_grupos.list_all(order_by=GrupoTarefas.denominacao)

    @staticmethod
    def get_group_detail(grupo_id: int) -> GrupoTarefas:
        """Fetches a specific group with its tasks."""
        repo_grupos = BaseRepository(GrupoTarefas)
        return repo_grupos.get_or_404(grupo_id)

    @staticmethod
    def create_task(descricao: str, grupo_id: Optional[int], current_user: Any) -> Optional[Tarefa]:
        status_pendente, _, _, grupo_comum = SeedService.init_tasks_defaults()
        if descricao:
            repo = BaseRepository(Tarefa)
            nova_tarefa = Tarefa(
                descricao=descricao.upper(),
                grupo_id=grupo_id if grupo_id else grupo_comum.id,
                status_id=status_pendente.id
            )
            repo.add(nova_tarefa)
            repo.commit()
            LogService.log_action(current_user.username, 'TASK_CREATED', f'ID: {nova_tarefa.id} | DESCRIPTION: {descricao}')
            return nova_tarefa
        return None

    @staticmethod
    def update_task_basic(id: int, descricao: Optional[str], grupo_id: Optional[int], status_nome: Optional[str], current_user: Any) -> Tarefa:
        repo = BaseRepository(Tarefa)
        tarefa = repo.get_or_404(id)
        
        if descricao:
            tarefa.descricao = descricao.upper()
        if grupo_id:
            tarefa.grupo_id = grupo_id
            
        if status_nome:
            status_pendente, status_iniciado, status_finalizado, _ = SeedService.init_tasks_defaults()
            sn = status_nome.upper()
            if sn == 'PENDENTE':
                tarefa.status_id = status_pendente.id
            elif sn == 'INICIADO':
                tarefa.status_id = status_iniciado.id
            elif sn == 'FINALIZADO':
                tarefa.status_id = status_finalizado.id
                tarefa.data_executado = datetime.now(timezone.utc)
                
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_EDITED', f'ID: {id} | NEW_DESCRIPTION: {descricao}')
        return tarefa

    @staticmethod
    def start_task(id: int, current_user: Any) -> Tarefa:
        repo = BaseRepository(Tarefa)
        tarefa = repo.get_or_404(id)
        _, status_iniciado, _, _ = SeedService.init_tasks_defaults()
        tarefa.status_id = status_iniciado.id
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_STARTED', f'ID: {id}')
        return tarefa

    @staticmethod
    def complete_task(id: int, current_user: Any) -> Tarefa:
        repo = BaseRepository(Tarefa)
        tarefa = repo.get_or_404(id)
        _, _, status_finalizado, _ = SeedService.init_tasks_defaults()
        tarefa.status_id = status_finalizado.id
        tarefa.data_executado = datetime.now(timezone.utc)
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_COMPLETED', f'ID: {id}')
        return tarefa

    @staticmethod
    def delete_task(id: int, current_user: Any) -> str:
        repo = BaseRepository(Tarefa)
        tarefa = repo.get_or_404(id)
        desc = tarefa.descricao
        repo.delete(tarefa)
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_DELETED', f'ID: {id} | DESCRIPTION: {desc}')
        return desc

    @staticmethod
    def create_group(denominacao: str, current_user: Any) -> Optional[GrupoTarefas]:
        if denominacao:
            repo = BaseRepository(GrupoTarefas)
            novo_grupo = GrupoTarefas(denominacao=denominacao.upper())
            repo.add(novo_grupo)
            repo.commit()
            LogService.log_action(current_user.username, 'TASK_GROUP_CREATED', f'NAME: {denominacao.upper()}')
            return novo_grupo
        return None

