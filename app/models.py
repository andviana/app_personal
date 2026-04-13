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

class Perfume(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    nome = db.mapped_column(db.String(100), nullable=False)
    marca = db.mapped_column(db.String(100), nullable=True)
    correspondente = db.mapped_column(db.String(100), nullable=True)
    valor = db.mapped_column(db.Float, nullable=True)
    url = db.mapped_column(db.String(500), nullable=True)
    url_imagem = db.mapped_column(db.String(500), nullable=True)
    data_cadastro = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Perfume {self.nome}>'

class Pessoa(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    nome_completo = db.mapped_column(db.String(150), nullable=False)
    rg_numero = db.mapped_column(db.String(20), nullable=True)
    rg_orgao = db.mapped_column(db.String(20), nullable=True)
    rg_data_expedicao = db.mapped_column(db.Date, nullable=True)
    cpf = db.mapped_column(db.String(14), nullable=True, unique=True)
    pis = db.mapped_column(db.String(14), nullable=True)
    data_nascimento = db.mapped_column(db.Date, nullable=True)
    foto_url = db.mapped_column(db.String(500), nullable=True)
    data_cadastro = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    enderecos = db.relationship('Endereco', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    telefones = db.relationship('Telefone', backref='pessoa', lazy=True, cascade="all, delete-orphan")
    arquivos = db.relationship('PessoaArquivo', backref='pessoa', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Pessoa {self.nome_completo}>'

class Endereco(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    descricao = db.mapped_column(db.String(255), nullable=False)

class Telefone(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    numero = db.mapped_column(db.String(20), nullable=False)

class PessoaArquivo(db.Model):
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    titulo = db.mapped_column(db.String(100), nullable=False)
    url = db.mapped_column(db.String(500), nullable=False)
