import uuid
from app import db
from datetime import datetime, timezone

# Tabela de associação Muitos-para-Muitos (Como Modelo para facilitar Backup)
class SnippetTag(db.Model):
    __tablename__ = 'snippet_tags'
    snippet_id = db.mapped_column(db.Integer, db.ForeignKey('snippet.id'), primary_key=True)
    tag_id = db.mapped_column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)

class Snippet(db.Model):
    """Armazenamento de pequenos trechos de texto ou código."""
    id = db.mapped_column(db.Integer, primary_key=True)
    uuid = db.mapped_column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    titulo = db.mapped_column(db.String(100), nullable=False)
    descricao = db.mapped_column(db.String(200), nullable=True)
    conteudo = db.mapped_column(db.Text, nullable=False)
    data_criacao = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamento com Tags
    tags = db.relationship('Tag', secondary='snippet_tags', back_populates='snippets', lazy='joined')

    def __repr__(self):
        return f'<Snippet {self.titulo}>'

class Tag(db.Model):
    """Etiquetas para categorização de snippets."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(50), nullable=False, unique=True)
    cor = db.mapped_column(db.String(20), nullable=False, default='#9a55f3')
    
    # Referência reversa
    snippets = db.relationship('Snippet', secondary='snippet_tags', back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.denominacao}>'

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
