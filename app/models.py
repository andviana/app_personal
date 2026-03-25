from datetime import datetime, timezone
from app import db

class GrupoTarefas(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    tarefas = db.relationship('Tarefa', backref='grupo', lazy=True)

class StatusTarefas(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(50), nullable=False)
    tarefas = db.relationship('Tarefa', backref='status', lazy=True)

class Tarefa(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    descricao = db.mapped_column(db.String(200), nullable=False)
    data_cadastro = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    data_executado = db.mapped_column(db.DateTime, nullable=True)
    status_id = db.mapped_column(db.Integer, db.ForeignKey('status_tarefas.id'), nullable=False)
    grupo_id = db.mapped_column(db.Integer, db.ForeignKey('grupo_tarefas.id'), nullable=False)



class TipoLista(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    listas = db.relationship('Lista', backref='tipo', lazy=True)

class GrupoItem(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    itens = db.relationship('ItemLista', backref='grupo', lazy=True)

class Lista(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    tipo_id = db.mapped_column(db.Integer, db.ForeignKey('tipo_lista.id'), nullable=False)
    itens = db.relationship('ItemLista', backref='lista', lazy=True, cascade="all, delete-orphan")

class ItemLista(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    lista_id = db.mapped_column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    item = db.mapped_column(db.String(150), nullable=False)
    grupo_id = db.mapped_column(db.Integer, db.ForeignKey('grupo_item.id'), nullable=True)
    link = db.mapped_column(db.String(500), nullable=True)
    valor = db.mapped_column(db.Float, nullable=True)
    status = db.mapped_column(db.Boolean, default=False) # True = comprado
