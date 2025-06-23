"""add notification prefs field to settings

Revision ID: 3c48a6fdd325
Revises: e0f7381c0a9f
Create Date: 2025-06-24 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '3c48a6fdd325'
down_revision: Union[str, None] = 'e0f7381c0a9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('settings', sa.Column(
        'notification_prefs',
        postgresql.JSONB(),
        nullable=False,
        server_default=sa.text("'{}'::jsonb")
    ))


def downgrade() -> None:
    op.drop_column('settings', 'notification_prefs')
