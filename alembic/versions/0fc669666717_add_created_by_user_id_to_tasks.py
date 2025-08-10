"""add created_by_user_id to tasks

Revision ID: 0fc669666717
Revises: 5c7f3042b1b1
Create Date: 2025-07-03 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0fc669666717'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('created_by_user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(
        'fk_tasks_created_by_user_id_users',
        'tasks', 'users', ['created_by_user_id'], ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_tasks_created_by_user_id_users', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'created_by_user_id')
