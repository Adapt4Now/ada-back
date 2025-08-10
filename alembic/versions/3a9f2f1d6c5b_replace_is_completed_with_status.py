"""replace is_completed with status

Revision ID: 3a9f2f1d6c5b
Revises: 5c7f3042b1b1
Create Date: 2025-07-06 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '3a9f2f1d6c5b'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status_enum = sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='taskstatus')
    status_enum.create(op.get_bind())
    op.add_column('tasks', sa.Column('status', status_enum, nullable=False, server_default='pending'))
    op.execute("UPDATE tasks SET status='completed' WHERE is_completed = TRUE")
    op.drop_column('tasks', 'is_completed')


def downgrade() -> None:
    op.add_column('tasks', sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.execute("UPDATE tasks SET is_completed = TRUE WHERE status='completed'")
    op.drop_column('tasks', 'status')
    status_enum = sa.Enum('pending', 'in_progress', 'completed', 'cancelled', name='taskstatus')
    status_enum.drop(op.get_bind())
