from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

# Association table between tasks and groups
# This file avoids circular imports by defining tables used in multiple modules

task_group_association = Table(
    'task_groups',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE"), primary_key=True),
)

# Association table between users and groups
user_group_membership = Table(
    'user_group_membership',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE"), primary_key=True),
)

# Association table between users and families (premium feature)
user_family_membership = Table(
    'user_family_membership',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete="CASCADE"), primary_key=True),
    Column('family_id', Integer, ForeignKey('families.id', ondelete="CASCADE"), primary_key=True),
)
