"""add premium flag and user-family membership

Revision ID: f66e5c3e972d
Revises: fb2d4edaf741
Create Date: 2025-06-24 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'f66e5c3e972d'
down_revision: Union[str, None] = 'fb2d4edaf741'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_premium', sa.Boolean(), nullable=False, server_default=sa.text('true')))

    op.create_table(
        'user_family_membership',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'family_id')
    )


def downgrade() -> None:
    op.drop_table('user_family_membership')
    op.drop_column('users', 'is_premium')
