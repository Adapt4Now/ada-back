"""add assigned_by_user_id to tasks

Revision ID: 5c7f3042b1b1
Revises: e0f7381c0a9f
Create Date: 2025-07-01 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '5c7f3042b1b1'
down_revision: Union[str, None] = 'e0f7381c0a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('assigned_by_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_tasks_assigned_by_user_id_users',
        'tasks', 'users', ['assigned_by_user_id'], ['id'], ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_tasks_assigned_by_user_id_users', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'assigned_by_user_id')
