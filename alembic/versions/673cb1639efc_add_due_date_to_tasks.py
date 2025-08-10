"""add due_date to tasks

Revision ID: 673cb1639efc
Revises: 5c7f3042b1b1
Create Date: 2025-08-10 09:31:07.135043

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '673cb1639efc'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('tasks', 'due_date')
