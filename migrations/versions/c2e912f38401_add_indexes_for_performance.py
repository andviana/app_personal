"""add_indexes_for_performance

Revision ID: c2e912f38401
Revises: c1f8342a198d
Create Date: 2026-09-17 00:11:30.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2e912f38401'
down_revision = 'c1f8342a198d'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    def safe_create_index(table_name, index_name, columns):
        if table_name in inspector.get_table_names():
            existing_indexes = [idx['name'] for idx in inspector.get_indexes(table_name)]
            if index_name not in existing_indexes:
                with op.batch_alter_table(table_name) as batch_op:
                    batch_op.create_index(index_name, columns)

    # 1. Bookmark Indexes
    safe_create_index('bookmark', 'ix_bookmark_owner_id', ['owner_id'])
    safe_create_index('bookmark_association', 'ix_bookmark_assoc_bookmark', ['bookmark_id'])
    safe_create_index('bookmark_association', 'ix_bookmark_assoc_category', ['category_id'])

    # 2. Lista & ItemLista Indexes
    safe_create_index('lista', 'ix_lista_owner_id', ['owner_id'])
    safe_create_index('lista', 'ix_lista_tipo_id', ['tipo_id'])
    safe_create_index('lista', 'ix_lista_is_active', ['is_active'])
    safe_create_index('item_lista', 'ix_item_lista_lista_id', ['lista_id'])
    safe_create_index('item_lista', 'ix_item_lista_grupo_id', ['grupo_id'])

    # 3. Tarefa & GrupoTarefas Indexes
    safe_create_index('tarefa', 'ix_tarefa_owner_id', ['owner_id'])
    safe_create_index('tarefa', 'ix_tarefa_grupo_id', ['grupo_id'])
    safe_create_index('tarefa', 'ix_tarefa_status_id', ['status_id'])
    safe_create_index('tarefa', 'ix_tarefa_is_active', ['is_active'])
    safe_create_index('grupo_tarefas', 'ix_grupo_tarefas_owner_id', ['owner_id'])
    safe_create_index('grupo_tarefas', 'ix_grupo_tarefas_is_active', ['is_active'])

    # 4. Snippet Indexes
    safe_create_index('snippet', 'ix_snippet_owner_id', ['owner_id'])


def downgrade():
    pass
