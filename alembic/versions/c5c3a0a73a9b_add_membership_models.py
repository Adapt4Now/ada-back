"""add membership models

Revision ID: c5c3a0a73a9b
Revises: 5c7f3042b1b1
Create Date: 2025-07-22 00:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c5c3a0a73a9b'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'group_memberships',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_table(
        'family_memberships',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'family_id')
    )
    op.execute(
        """
        INSERT INTO group_memberships (user_id, group_id, role, joined_at)
        SELECT user_id, group_id, 'member', now() FROM user_group_membership
        """
    )
    op.execute(
        """
        INSERT INTO family_memberships (user_id, family_id, role, joined_at)
        SELECT user_id, family_id, 'member', now() FROM user_family_membership
        """
    )
    op.drop_table('user_group_membership')
    op.drop_table('user_family_membership')


def downgrade() -> None:
    op.create_table(
        'user_group_membership',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )
    op.create_table(
        'user_family_membership',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'family_id')
    )
    op.execute(
        """
        INSERT INTO user_group_membership (user_id, group_id)
        SELECT user_id, group_id FROM group_memberships
        """
    )
    op.execute(
        """
        INSERT INTO user_family_membership (user_id, family_id)
        SELECT user_id, family_id FROM family_memberships
        """
    )
    op.drop_table('group_memberships')
    op.drop_table('family_memberships')
