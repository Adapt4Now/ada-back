"""add email verification fields to users

Revision ID: 8b1e2f91e9e7
Revises: 5c7f3042b1b1
Create Date: 2025-07-05 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8b1e2f91e9e7'
down_revision: Union[str, None] = '5c7f3042b1b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'is_email_verified')
