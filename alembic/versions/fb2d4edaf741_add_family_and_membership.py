"""add family table and group membership"""

revision = 'fb2d4edaf741'
down_revision = '3c48a6fdd325'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        'families',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('name'),
    )
    op.create_foreign_key('fk_families_created_by_users', 'families', 'users', ['created_by'], ['id'])

    op.add_column('users', sa.Column('family_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_users_family', 'users', 'families', ['family_id'], ['id'])

    op.add_column('groups', sa.Column('family_id', sa.Integer(), nullable=False))
    op.create_foreign_key('fk_groups_family', 'groups', 'families', ['family_id'], ['id'])
    op.create_unique_constraint('uq_groups_family_name', 'groups', ['family_id', 'name'])
    op.drop_column('groups', 'user_ids')

    op.create_table(
        'user_group_membership',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'group_id')
    )


def downgrade() -> None:
    op.drop_table('user_group_membership')
    op.add_column('groups', sa.Column('user_ids', sa.ARRAY(sa.Integer()), nullable=False, server_default=sa.text("'{}'")))
    op.drop_constraint('fk_groups_family', 'groups', type_='foreignkey')
    op.drop_constraint('uq_groups_family_name', 'groups', type_='unique')
    op.drop_column('groups', 'family_id')
    op.drop_constraint('fk_users_family', 'users', type_='foreignkey')
    op.drop_column('users', 'family_id')
    op.drop_constraint('fk_families_created_by_users', 'families', type_='foreignkey')
    op.drop_table('families')
