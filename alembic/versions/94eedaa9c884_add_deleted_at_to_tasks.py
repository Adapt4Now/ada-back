"""add deleted_at to tasks

Revision ID: 94eedaa9c884
Revises: 5c7f3042b1b1
Create Date: 2025-08-10 09:31:25.600708

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94eedaa9c884'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tasks',
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        'tasks',
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='false')
    )


def downgrade() -> None:
    op.drop_column('tasks', 'is_archived')
    op.drop_column('tasks', 'deleted_at')
