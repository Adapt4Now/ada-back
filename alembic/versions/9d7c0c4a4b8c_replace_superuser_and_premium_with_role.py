"""replace superuser and premium with role

Revision ID: 9d7c0c4a4b8c
Revises: e0f7381c0a9f
Create Date: 2025-08-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d7c0c4a4b8c"
down_revision: Union[str, None] = "e0f7381c0a9f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userrole = sa.Enum("USER", "PREMIUM", "ADMIN", name="userrole")
    userrole.create(op.get_bind(), checkfirst=True)
    op.add_column("users", sa.Column("role", userrole, nullable=False, server_default="USER"))

    op.execute("UPDATE users SET role = 'ADMIN' WHERE is_superuser = TRUE")
    op.execute("UPDATE users SET role = 'PREMIUM' WHERE role = 'USER' AND is_premium = TRUE")

    op.drop_column("users", "is_superuser")
    op.drop_column("users", "is_premium")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_premium", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column(
        "users",
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.execute(
        "UPDATE users SET is_superuser = CASE WHEN role = 'ADMIN' THEN TRUE ELSE FALSE END"
    )
    op.execute(
        "UPDATE users SET is_premium = CASE WHEN role IN ('PREMIUM','ADMIN') THEN TRUE ELSE FALSE END"
    )

    op.drop_column("users", "role")
    userrole = sa.Enum("USER", "PREMIUM", "ADMIN", name="userrole")
    userrole.drop(op.get_bind(), checkfirst=True)

