from app import db
from datetime import datetime, timezone, date

class Pessoa(db.Model):
    """Cadastro central de pessoas e documentos."""
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

    @property
    def idade(self):
        if not self.data_nascimento:
            return None
        today = date.today()
        return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))

    def __repr__(self):
        return f'<Pessoa {self.nome_completo}>'

class Endereco(db.Model):
    """Endereços vinculados a uma pessoa."""
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    descricao = db.mapped_column(db.String(255), nullable=False)

class Telefone(db.Model):
    """Números de telefone vinculados a uma pessoa."""
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    numero = db.mapped_column(db.String(20), nullable=False)

class PessoaArquivo(db.Model):
    """Arquivos e documentos digitais vinculados a uma pessoa."""
    id = db.mapped_column(db.Integer, primary_key=True)
    pessoa_id = db.mapped_column(db.Integer, db.ForeignKey('pessoa.id'), nullable=False)
    titulo = db.mapped_column(db.String(100), nullable=False)
    url = db.mapped_column(db.String(500), nullable=False)
