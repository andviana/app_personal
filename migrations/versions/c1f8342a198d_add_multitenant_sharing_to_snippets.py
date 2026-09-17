"""add_multitenant_sharing_to_snippets

Revision ID: c1f8342a198d
Revises: b7e8912c345a
Create Date: 2026-09-16 23:57:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c1f8342a198d'
down_revision = 'b7e8912c345a'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Add owner_id to snippet table if it doesn't exist
    columns = [c['name'] for c in inspector.get_columns('snippet')]
    with op.batch_alter_table('snippet', schema=None) as batch_op:
        if 'owner_id' not in columns:
            batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_snippet_owner', 'user', ['owner_id'], ['id'])

    # 2. Create shared_snippets table if it doesn't exist
    tables = inspector.get_table_names()
    if 'shared_snippets' not in tables:
        op.create_table(
            'shared_snippets',
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
            sa.Column('snippet_id', sa.Integer(), sa.ForeignKey('snippet.id', ondelete='CASCADE'), primary_key=True)
        )

    # 3. Ensure user 'anderson' exists
    user_res = bind.execute(sa.text('SELECT id FROM "user" WHERE username = \'anderson\'')).fetchone()
    if user_res:
        anderson_id = user_res[0]
    else:
        from werkzeug.security import generate_password_hash
        pwd_hash = generate_password_hash("anderson123")
        bind.execute(
            sa.text('INSERT INTO "user" (username, password_hash) VALUES (:u, :p)'),
            {"u": "anderson", "p": pwd_hash}
        )
        user_res = bind.execute(sa.text('SELECT id FROM "user" WHERE username = \'anderson\'')).fetchone()
        anderson_id = user_res[0]

    # 4. Link all existing snippets without owner_id to 'anderson'
    bind.execute(
        sa.text("UPDATE snippet SET owner_id = :aid WHERE owner_id IS NULL"),
        {"aid": anderson_id}
    )


def downgrade():
    pass
