from app import db
from app.models import StatusTarefas, GrupoTarefas

class SeedService:
    @staticmethod
    def init_tasks_defaults():
        """
        Garante que os status e grupos básicos de tarefas existam no banco.
        Retorna (status_pendente, status_iniciado, status_finalizado, grupo_comum)
        """
        # Usamos filter_by().first() que é eficiente
        status_pendente = StatusTarefas.query.filter_by(denominacao='PENDENTE').first()
        status_iniciado = StatusTarefas.query.filter_by(denominacao='INICIADO').first()
        status_finalizado = StatusTarefas.query.filter_by(denominacao='FINALIZADO').first()
        grupo_comum = GrupoTarefas.query.filter_by(denominacao='COMUM').first()

        changed = False
        if not status_pendente:
            status_pendente = StatusTarefas(denominacao='PENDENTE')
            db.session.add(status_pendente)
            changed = True
        
        if not status_iniciado:
            status_iniciado = StatusTarefas(denominacao='INICIADO')
            db.session.add(status_iniciado)
            changed = True

        if not status_finalizado:
            status_finalizado = StatusTarefas(denominacao='FINALIZADO')
            db.session.add(status_finalizado)
            changed = True

        if not grupo_comum:
            grupo_comum = GrupoTarefas(denominacao='COMUM')
            db.session.add(grupo_comum)
            changed = True

        if changed:
            db.session.commit()

        return status_pendente, status_iniciado, status_finalizado, grupo_comum
