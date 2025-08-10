"""add reward_points_to_tasks

Revision ID: a2a8cfb93f7b
Revises: 5c7f3042b1b1
Create Date: 2025-08-10 09:32:26.269276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2a8cfb93f7b'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tasks',
        sa.Column('reward_points', sa.Integer(), nullable=False, server_default=sa.text('0'))
    )
    op.alter_column('tasks', 'reward_points', server_default=None)


def downgrade() -> None:
    op.drop_column('tasks', 'reward_points')
