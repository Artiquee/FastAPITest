"""add blocked column to comments

Revision ID: 8dcea9dde53d
Revises: bc680541a304
Create Date: 2024-10-31 19:30:36.155449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dcea9dde53d'
down_revision: Union[str, None] = 'bc680541a304'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('comments', sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='false'))


def downgrade():
    op.drop_column('comments', 'is_blocked')
