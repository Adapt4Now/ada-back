"""add user status

Revision ID: 2c0c26e660d5
Revises: 5c7f3042b1b1
Create Date: 2024-04-19 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0c26e660d5'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum = sa.Enum('ACTIVE', 'PENDING', 'SUSPENDED', 'BANNED', name='userstatus')
    status_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('users', sa.Column('status', status_enum, nullable=False, server_default='ACTIVE'))


def downgrade() -> None:
    op.drop_column('users', 'status')
    status_enum = sa.Enum('ACTIVE', 'PENDING', 'SUSPENDED', 'BANNED', name='userstatus')
    status_enum.drop(op.get_bind(), checkfirst=True)

