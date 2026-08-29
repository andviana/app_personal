from app import db
from datetime import datetime, timezone

shared_tasks = db.Table(
    'shared_tasks',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('tarefa_id', db.Integer, db.ForeignKey('tarefa.id', ondelete='CASCADE'), primary_key=True)
)

class GrupoTarefas(db.Model):
    """Categorização de tarefas (ex: Trabalho, Pessoal)."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    tarefas = db.relationship('Tarefa', backref='grupo', lazy=True)

    @property
    def tarefas_filtradas(self):
        if hasattr(self, '_tarefas_filtradas'):
            return self._tarefas_filtradas
        return self.tarefas

    @tarefas_filtradas.setter
    def tarefas_filtradas(self, val):
        self._tarefas_filtradas = val

class StatusTarefas(db.Model):
    """Estados possíveis para uma tarefa (PENDENTE, INICIADO, FINALIZADO)."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(50), nullable=False)
    tarefas = db.relationship('Tarefa', backref='status', lazy=True)

class Tarefa(db.Model):
    """Entidade de tarefa individual."""
    id = db.mapped_column(db.Integer, primary_key=True)
    descricao = db.mapped_column(db.String(200), nullable=False)
    data_cadastro = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_executado = db.mapped_column(db.DateTime, nullable=True)
    status_id = db.mapped_column(db.Integer, db.ForeignKey('status_tarefas.id'), nullable=False)
    grupo_id = db.mapped_column(db.Integer, db.ForeignKey('grupo_tarefas.id'), nullable=False)
    owner_id = db.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.mapped_column(db.Boolean, default=True, nullable=False)

    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_tasks')
    shared_users = db.relationship('User', secondary=shared_tasks, backref='shared_tasks')

