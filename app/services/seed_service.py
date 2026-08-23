from app.repositories.task_repository import StatusTarefasRepository, GrupoTarefasRepository
from app.models import StatusTarefas, GrupoTarefas

class SeedService:
    @staticmethod
    def init_tasks_defaults():
        """
        Garante que os status e grupos básicos de tarefas existam no banco.
        Retorna (status_pendente, status_iniciado, status_finalizado, grupo_comum)
        """
        repo_status = StatusTarefasRepository()
        repo_grupo = GrupoTarefasRepository()

        status_pendente = repo_status.find_by_denominacao('PENDENTE')
        status_iniciado = repo_status.find_by_denominacao('INICIADO')
        status_finalizado = repo_status.find_by_denominacao('FINALIZADO')
        grupo_comum = repo_grupo.find_by_denominacao('COMUM')

        changed = False
        if not status_pendente:
            status_pendente = StatusTarefas(denominacao='PENDENTE')
            repo_status.add(status_pendente)
            changed = True
        
        if not status_iniciado:
            status_iniciado = StatusTarefas(denominacao='INICIADO')
            repo_status.add(status_iniciado)
            changed = True

        if not status_finalizado:
            status_finalizado = StatusTarefas(denominacao='FINALIZADO')
            repo_status.add(status_finalizado)
            changed = True

        if not grupo_comum:
            grupo_comum = GrupoTarefas(denominacao='COMUM')
            repo_grupo.add(grupo_comum)
            changed = True

        if changed:
            repo_status.commit()

        return status_pendente, status_iniciado, status_finalizado, grupo_comum
