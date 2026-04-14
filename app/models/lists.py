from app import db

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
    tipo_id = db.mapped_column(db.Integer, db.ForeignKey('tipo_lista.id'), nullable=False)
    itens = db.relationship('ItemLista', backref='lista', lazy=True, cascade="all, delete-orphan")

class ItemLista(db.Model):
    """Item individual pertencente a uma lista."""
    id = db.mapped_column(db.Integer, primary_key=True)
    lista_id = db.mapped_column(db.Integer, db.ForeignKey('lista.id'), nullable=False)
    item = db.mapped_column(db.String(150), nullable=False)
    grupo_id = db.mapped_column(db.Integer, db.ForeignKey('grupo_item.id'), nullable=True)
    link = db.mapped_column(db.String(500), nullable=True)
    valor = db.mapped_column(db.Float, nullable=True)
    status = db.mapped_column(db.Boolean, default=False) # True = comprado/concluído
