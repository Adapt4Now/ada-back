from typing import List, Optional, cast
from sqlalchemy.orm import Session
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate


def create_group(db: Session, group: GroupCreate, created_by: str) -> Group:
    """Create a new group."""
    db_group = Group(
        name=group.name,
        description=group.description,
        created_by=created_by,
        user_ids=group.user_ids,
        is_active=True
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_group(
    db: Session, 
    group_id: int, 
    active_only: bool = True
) -> Optional[Group]:
    """Get a group by ID."""
    query = db.query(Group)
    if active_only:
        query = query.filter(Group.is_active.is_(True))
    return query.filter(Group.id == group_id).first()


def get_groups(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True
) -> List[Group]:
    """Get a list of groups with pagination."""
    query = db.query(Group)
    if active_only:
        query = query.filter(Group.is_active.is_(True))
    result = query.order_by(Group.id).offset(skip).limit(limit).all()
    return cast(List[Group], result)


def update_group(
    db: Session, 
    group_id: int, 
    group_update: GroupUpdate
) -> Optional[Group]:
    """Update a group by ID."""
    db_group = get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)

    db.commit()
    db.refresh(db_group)
    return db_group


def delete_group(
    db: Session, 
    group_id: int, 
    hard_delete: bool = False
) -> Optional[Group]:
    """Delete a group by ID."""
    db_group = get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    if hard_delete:
        db.delete(db_group)
    else:
        db_group.is_active = False

    db.commit()
    return db_group


def get_groups_by_user(
    db: Session, 
    user_id: int, 
    active_only: bool = True
) -> List[Group]:
    """Get all groups that a user belongs to."""
    query = db.query(Group).filter(Group.user_ids.contains([user_id]))
    if active_only:
        query = query.filter(Group.is_active.is_(True))
    result = query.order_by(Group.id).all()
    return cast(List[Group], result)


def add_users_to_group(
    db: Session, 
    group_id: int, 
    user_ids: List[int]
) -> Optional[Group]:
    """Add users to a group."""
    db_group = get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    # Add new users without duplicates
    existing_users = set(db_group.user_ids)
    new_users = set(user_ids)
    db_group.user_ids = list(existing_users | new_users)

    db.commit()
    db.refresh(db_group)
    return db_group


def remove_users_from_group(
    db: Session, 
    group_id: int, 
    user_ids: List[int]
) -> Optional[Group]:
    """Remove users from a group."""
    db_group = get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    # Remove specified users
    users_to_remove = set(user_ids)
    db_group.user_ids = [
        uid for uid in db_group.user_ids 
        if uid not in users_to_remove
    ]

    db.commit()
    db.refresh(db_group)
    return db_group