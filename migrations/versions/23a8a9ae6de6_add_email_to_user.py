"""add_email_to_user

Revision ID: 23a8a9ae6de6
Revises: 94fb13dc5041
Create Date: 2026-08-30 16:02:45.423100

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '23a8a9ae6de6'
down_revision = '94fb13dc5041'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = [c['name'] for c in inspector.get_columns('user')]

    if 'email' not in user_cols:
        with op.batch_alter_table('user', schema=None) as batch_op:
            batch_op.add_column(sa.Column('email', sa.String(length=255), nullable=True))
            batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email'))
        batch_op.drop_column('email')
