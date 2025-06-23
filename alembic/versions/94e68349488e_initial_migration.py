"""Initial migration

Revision ID: 94e68349488e
Revises: 
Create Date: 2025-06-22 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '94e68349488e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
    )

    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('user_ids', postgresql.ARRAY(sa.Integer()), nullable=False, server_default=sa.text("'{}'")),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('assigned_user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['assigned_user_id'], ['users.id'], ondelete='SET NULL'),
    )

    op.create_table(
        'task_groups',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'group_id')
    )

    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False, unique=True),
        sa.Column('theme', sa.String(length=50), nullable=False, server_default='light'),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )


def downgrade() -> None:
    op.drop_table('notifications')
    op.drop_table('settings')
    op.drop_table('task_groups')
    op.drop_table('tasks')
    op.drop_table('groups')
    op.drop_table('users')
