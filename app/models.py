from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    username = db.mapped_column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.mapped_column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

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

class Snippet(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    titulo = db.mapped_column(db.String(100), nullable=False)
    descricao = db.mapped_column(db.String(200), nullable=True)
    conteudo = db.mapped_column(db.Text, nullable=False)
    data_criacao = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Snippet {self.titulo}>'
