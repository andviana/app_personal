from datetime import datetime, timezone
from typing import List, Optional, Any
from app.repositories.task_repository import TaskRepository, GrupoTarefasRepository
from app.models import Tarefa, GrupoTarefas, User
from app.services.log_service import LogService
from app.services.seed_service import SeedService

class TaskService:
    @staticmethod
    def can_write(tarefa: Tarefa, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        # Direct owner or direct shared user
        if tarefa.owner_id == current_user.id or any(u.id == current_user.id for u in tarefa.shared_users):
            return True
        # Inherited from group owner or group shared user
        if tarefa.grupo:
            if tarefa.grupo.owner_id == current_user.id or any(u.id == current_user.id for u in tarefa.grupo.shared_users):
                return True
        return False

    @staticmethod
    def can_manage(tarefa: Tarefa, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return tarefa.owner_id == current_user.id

    @staticmethod
    def can_read_group(grupo: GrupoTarefas, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return grupo.owner_id == current_user.id or any(u.id == current_user.id for u in grupo.shared_users)

    @staticmethod
    def can_write_group(grupo: GrupoTarefas, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return grupo.owner_id == current_user.id or any(u.id == current_user.id for u in grupo.shared_users)

    @staticmethod
    def can_manage_group(grupo: GrupoTarefas, current_user: Any) -> bool:
        if not current_user or not current_user.is_authenticated:
            return False
        return grupo.owner_id == current_user.id

    @staticmethod
    def get_all_tasks(current_user: Any, is_active: bool = True) -> List[Tarefa]:
        repo = TaskRepository()
        return repo.list_user_tasks(current_user.id, is_active=is_active)

    @staticmethod
    def get_tasks_data(current_user: Any, is_active: bool = True) -> List[GrupoTarefas]:
        """Fetches all groups with user's filtered tasks."""
        SeedService.init_tasks_defaults()
        repo_grupos = GrupoTarefasRepository()
        repo_tasks = TaskRepository()
        
        grupos = repo_grupos.list_user_groups(current_user.id, is_active=is_active)
        user_tasks = repo_tasks.list_user_tasks(current_user.id, is_active=is_active)

        status_priority = {'INICIADO': 0, 'PENDENTE': 1, 'FINALIZADO': 2}
        for g in grupos:
            g.tarefas_filtradas = [t for t in user_tasks if t.grupo_id == g.id]
            g.tarefas_filtradas.sort(key=lambda t: status_priority.get(t.status.denominacao.upper() if t.status else 'PENDENTE', 9))
        return grupos

    @staticmethod
    def get_all_groups(current_user: Any, is_active: bool = True) -> List[GrupoTarefas]:
        """Fetches all groups with task counts filtered for user."""
        SeedService.init_tasks_defaults()
        repo_grupos = GrupoTarefasRepository()
        repo_tasks = TaskRepository()
        
        grupos = repo_grupos.list_user_groups(current_user.id, is_active=is_active)
        user_tasks = repo_tasks.list_user_tasks(current_user.id, is_active=is_active)

        for g in grupos:
            g.tarefas_filtradas = [t for t in user_tasks if t.grupo_id == g.id]
        return grupos

    @staticmethod
    def get_group_detail(grupo_id: int, current_user: Any, is_active: bool = True) -> GrupoTarefas:
        """Fetches a specific group with user's filtered tasks."""
        repo_grupos = GrupoTarefasRepository()
        repo_tasks = TaskRepository()
        
        grupo = repo_grupos.get_or_404(grupo_id)
        if not TaskService.can_read_group(grupo, current_user):
            # Check if user has task access inside group
            user_tasks = repo_tasks.list_user_tasks(current_user.id, is_active=is_active, grupo_id=grupo_id)
            if not user_tasks:
                raise PermissionError("Sem permissão para visualizar este grupo.")
        else:
            user_tasks = repo_tasks.list_user_tasks(current_user.id, is_active=is_active, grupo_id=grupo_id)

        status_priority = {'INICIADO': 0, 'PENDENTE': 1, 'FINALIZADO': 2}
        user_tasks.sort(key=lambda t: status_priority.get(t.status.denominacao.upper() if t.status else 'PENDENTE', 9))
        grupo.tarefas_filtradas = user_tasks
        return grupo

    @staticmethod
    def create_task(descricao: str, grupo_id: Optional[int], current_user: Any) -> Optional[Tarefa]:
        status_pendente, _, _, grupo_comum = SeedService.init_tasks_defaults()
        if descricao:
            repo = TaskRepository()
            nova_tarefa = Tarefa(
                descricao=descricao.upper(),
                grupo_id=grupo_id if grupo_id else grupo_comum.id,
                status_id=status_pendente.id,
                owner_id=current_user.id,
                is_active=True
            )
            repo.add(nova_tarefa)
            repo.commit()
            LogService.log_action(current_user.username, 'TASK_CREATED', f'ID: {nova_tarefa.id} | DESCRIPTION: {descricao}')
            return nova_tarefa
        return None

    @staticmethod
    def update_task_basic(id: int, descricao: Optional[str], grupo_id: Optional[int], status_nome: Optional[str], current_user: Any) -> Tarefa:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        
        if not TaskService.can_write(tarefa, current_user):
            raise PermissionError("Sem permissão para editar esta tarefa.")
        
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
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_write(tarefa, current_user):
            raise PermissionError("Sem permissão para alterar o status desta tarefa.")
        _, status_iniciado, _, _ = SeedService.init_tasks_defaults()
        tarefa.status_id = status_iniciado.id
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_STARTED', f'ID: {id}')
        return tarefa

    @staticmethod
    def complete_task(id: int, current_user: Any) -> Tarefa:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_write(tarefa, current_user):
            raise PermissionError("Sem permissão para concluir esta tarefa.")
        _, _, status_finalizado, _ = SeedService.init_tasks_defaults()
        tarefa.status_id = status_finalizado.id
        tarefa.data_executado = datetime.now(timezone.utc)
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_COMPLETED', f'ID: {id}')
        return tarefa

    @staticmethod
    def delete_task(id: int, current_user: Any) -> str:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_manage(tarefa, current_user):
            raise PermissionError("Apenas o proprietário pode excluir esta tarefa.")
        desc = tarefa.descricao
        repo.delete(tarefa)
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_DELETED', f'ID: {id} | DESCRIPTION: {desc}')
        return desc

    @staticmethod
    def archive_task(id: int, current_user: Any) -> Tarefa:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_manage(tarefa, current_user):
            raise PermissionError("Apenas o proprietário pode arquivar esta tarefa.")
        tarefa.is_active = False
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_ARCHIVED', f'ID: {id}')
        return tarefa

    @staticmethod
    def reactivate_task(id: int, current_user: Any) -> Tarefa:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_manage(tarefa, current_user):
            raise PermissionError("Apenas o proprietário pode reativar esta tarefa.")
        tarefa.is_active = True
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_REACTIVATED', f'ID: {id}')
        return tarefa

    @staticmethod
    def share_task(id: int, user_ids: List[int], current_user: Any) -> Tarefa:
        repo = TaskRepository()
        tarefa = repo.get_or_404(id)
        if not TaskService.can_manage(tarefa, current_user):
            raise PermissionError("Apenas o proprietário pode compartilhar esta tarefa.")
        
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
        tarefa.shared_users = [u for u in users if u.id != tarefa.owner_id]
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_SHARED', f'ID: {id} | SHARED_WITH: {[u.username for u in tarefa.shared_users]}')
        return tarefa

    @staticmethod
    def create_group(denominacao: str, current_user: Any) -> Optional[GrupoTarefas]:
        if denominacao:
            repo = GrupoTarefasRepository()
            novo_grupo = GrupoTarefas(
                denominacao=denominacao.upper(),
                owner_id=current_user.id,
                is_active=True
            )
            repo.add(novo_grupo)
            repo.commit()
            LogService.log_action(current_user.username, 'TASK_GROUP_CREATED', f'NAME: {denominacao.upper()}')
            return novo_grupo
        return None

    @staticmethod
    def delete_group(id: int, current_user: Any) -> str:
        repo = GrupoTarefasRepository()
        grupo = repo.get_or_404(id)
        if not TaskService.can_manage_group(grupo, current_user):
            raise PermissionError("Apenas o proprietário pode excluir este grupo.")
        nome = grupo.denominacao
        repo.delete(grupo)
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_GROUP_DELETED', f'ID: {id} | NAME: {nome}')
        return nome

    @staticmethod
    def archive_group(id: int, current_user: Any) -> GrupoTarefas:
        repo = GrupoTarefasRepository()
        grupo = repo.get_or_404(id)
        if not TaskService.can_manage_group(grupo, current_user):
            raise PermissionError("Apenas o proprietário pode arquivar este grupo.")
        grupo.is_active = False
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_GROUP_ARCHIVED', f'ID: {id}')
        return grupo

    @staticmethod
    def reactivate_group(id: int, current_user: Any) -> GrupoTarefas:
        repo = GrupoTarefasRepository()
        grupo = repo.get_or_404(id)
        if not TaskService.can_manage_group(grupo, current_user):
            raise PermissionError("Apenas o proprietário pode reativar este grupo.")
        grupo.is_active = True
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_GROUP_REACTIVATED', f'ID: {id}')
        return grupo

    @staticmethod
    def share_group(id: int, user_ids: List[int], current_user: Any) -> GrupoTarefas:
        repo = GrupoTarefasRepository()
        grupo = repo.get_or_404(id)
        if not TaskService.can_manage_group(grupo, current_user):
            raise PermissionError("Apenas o proprietário pode compartilhar este grupo.")
        
        users = User.query.filter(User.id.in_(user_ids)).all() if user_ids else []
        grupo.shared_users = [u for u in users if u.id != grupo.owner_id]
        repo.commit()
        LogService.log_action(current_user.username, 'TASK_GROUP_SHARED', f'ID: {id} | SHARED_WITH: {[u.username for u in grupo.shared_users]}')
        return grupo

