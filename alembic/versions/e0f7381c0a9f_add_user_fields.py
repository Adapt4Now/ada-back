"""add user fields

Revision ID: e0f7381c0a9f
Revises: 
Create Date: 2025-06-23 15:19:47.886426

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e0f7381c0a9f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('users', sa.Column('first_name', sa.String(length=150), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(length=150), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('locale', sa.String(length=20), nullable=False, server_default=sa.text("'en-US'")))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=False, server_default=sa.text("'UTC'")))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('points', sa.Integer(), nullable=False, server_default=sa.text('0')))
    op.add_column('users', sa.Column('level', sa.SmallInteger(), nullable=True))
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('created_by', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_created_by_users', 'users', 'users', ['created_by'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_users_created_by_users', 'users', type_='foreignkey')
    op.drop_column('users', 'created_by')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'level')
    op.drop_column('users', 'points')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'locale')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'last_name')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'is_superuser')
