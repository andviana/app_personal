from app import db

shared_lists = db.Table(
    'shared_lists',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('lista_id', db.Integer, db.ForeignKey('lista.id', ondelete='CASCADE'), primary_key=True)
)

shared_simple_lists = db.Table(
    'shared_simple_lists',
    db.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('lista_id', db.Integer, db.ForeignKey('lista.id', ondelete='CASCADE'), primary_key=True)
)

class TipoLista(db.Model):
    """Tipo de lista (ex: Compras, Desejos, Filmes)."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    listas = db.relationship('Lista', backref='tipo', lazy=True)

class GrupoItem(db.Model):
    """Agrupamento de itens dentro de uma lista (ex: Mercado, Padaria)."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    itens = db.relationship('ItemLista', backref='grupo', lazy=True)

class Lista(db.Model):
    """Entidade representativa de uma lista de itens."""
    id = db.mapped_column(db.Integer, primary_key=True)
    denominacao = db.mapped_column(db.String(100), nullable=False)
    tipo_id = db.mapped_column(db.Integer, db.ForeignKey('tipo_lista.id'), nullable=True)
    owner_id = db.mapped_column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.mapped_column(db.Boolean, default=True, nullable=False)

    itens = db.relationship('ItemLista', backref='lista', lazy=True, cascade="all, delete-orphan")
    owner = db.relationship('User', foreign_keys=[owner_id], backref='owned_lists')
    shared_users = db.relationship('User', secondary=shared_lists, backref='shared_lists')
    shared_simple_users = db.relationship('User', secondary=shared_simple_lists, backref='shared_simple_lists')

    @property
    def shared_with_users(self):
        return self.shared_simple_users if self.tipo_id is None else self.shared_users

class ItemLista(db.Model):
    """Item individual pertencente a uma lista."""
    id = db.mapped_column(db.Integer, primary_key=True)
    lista_id = db.mapped_column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    item = db.mapped_column(db.String(150), nullable=False)
    grupo_id = db.mapped_column(db.Integer, db.ForeignKey('grupo_item.id'), nullable=True)
    link = db.mapped_column(db.String(500), nullable=True)
    valor = db.mapped_column(db.Float, nullable=True)
    status = db.mapped_column(db.Boolean, default=False) # True = comprado/concluído

