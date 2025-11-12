# alembic/script.py.mako
"""Add test data

Revision ID: 63fac8a08259
Revises: 9b9fdca32c17
Create Date: 2025-11-11 16:52:50.215402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '63fac8a08259'
down_revision = '9b9fdca32c17'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO users (name, api_key) VALUES 
        ('OLIVER', 'test'),
        ('Jenia', '123'), 
        ('Gavan Jordg', '000')
    """)

def downgrade() -> None:
    op.execute("DELETE FROM users WHERE api_key IN ('test', '123', '000')")