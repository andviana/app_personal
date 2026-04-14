from app import db
from datetime import datetime, timezone

class Snippet(db.Model):
    """Armazenamento de pequenos trechos de texto ou código."""
    id = db.mapped_column(db.Integer, primary_key=True)
    titulo = db.mapped_column(db.String(100), nullable=False)
    descricao = db.mapped_column(db.String(200), nullable=True)
    conteudo = db.mapped_column(db.Text, nullable=False)
    data_criacao = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f'<Snippet {self.titulo}>'

class Perfume(db.Model):
    """Catálogo de perfumes e fragrâncias."""
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
