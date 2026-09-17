"""link_bookmarks_to_anderson

Revision ID: b7e8912c345a
Revises: 23a8a9ae6de6
Create Date: 2026-09-16 23:43:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7e8912c345a'
down_revision = '23a8a9ae6de6'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    
    # Ensure user 'anderson' exists
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

    # Update existing unowned bookmarks
    bind.execute(
        sa.text("UPDATE bookmark SET owner_id = :aid WHERE owner_id IS NULL"),
        {"aid": anderson_id}
    )


def downgrade():
    pass
