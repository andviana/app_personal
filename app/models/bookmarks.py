from app import db
from datetime import datetime, timezone

shared_bookmarks = db.Table(
    'shared_bookmarks',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('bookmark_id', db.Integer, db.ForeignKey('bookmark.id', ondelete='CASCADE'), primary_key=True)
)

# Tabela de associação Muitos-para-Muitos (Como Modelo para facilitar Backup)
class BookmarkAssociation(db.Model):
    __tablename__ = 'bookmark_association'
    bookmark_id = db.mapped_column(db.Integer, db.ForeignKey('bookmark.id'), primary_key=True)
    category_id = db.mapped_column(db.Integer, db.ForeignKey('bookmark_category.id'), primary_key=True)

class BookmarkCategory(db.Model):
    __tablename__ = 'bookmark_category'
    id = db.mapped_column(db.Integer, primary_key=True)
    nome = db.mapped_column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f'<BookmarkCategory {self.nome}>'

class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    id = db.mapped_column(db.Integer, primary_key=True)
    titulo = db.mapped_column(db.String(200), nullable=False)
    url = db.mapped_column(db.String(500), nullable=False)
    image_url = db.mapped_column(db.String(500), nullable=True)
    descricao = db.mapped_column(db.Text, nullable=True)
    data_criacao = db.mapped_column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = db.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.mapped_column(db.Boolean, default=True, nullable=False)
    
    # Relacionamento com Categorias e Usuários
    categories = db.relationship('BookmarkCategory', secondary='bookmark_association', backref='bookmarks')
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_bookmarks')
    shared_users = db.relationship('User', secondary=shared_bookmarks, backref='shared_bookmarks')

    def __repr__(self):
        return f'<Bookmark {self.titulo}>'
