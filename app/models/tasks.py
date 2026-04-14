from app import db
from datetime import datetime, timezone

class GrupoTarefas(db.Model):
    """Categorização de tarefas (ex: Trabalho, Pessoal)."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    tarefas = db.relationship('Tarefa', backref='grupo', lazy=True)

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
