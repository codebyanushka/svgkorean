import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.group import Group, GroupMember
from app.models.user import Role, User


def list_students_for_teacher(db: Session, teacher_id: uuid.UUID) -> list[User]:
    group_ids = db.scalars(select(Group.id).where(Group.teacher_id == teacher_id)).all()
    if not group_ids:
        return []
    student_ids = db.scalars(select(GroupMember.user_id).where(GroupMember.group_id.in_(group_ids))).all()
    if not student_ids:
        return []
    return list(db.scalars(select(User).where(User.id.in_(student_ids), User.role == Role.STUDENT)))


def is_student_assigned_to_teacher(db: Session, teacher_id: uuid.UUID, student_id: uuid.UUID) -> bool:
    group_ids = db.scalars(select(Group.id).where(Group.teacher_id == teacher_id)).all()
    if not group_ids:
        return False
    membership = db.scalars(
        select(GroupMember.id).where(GroupMember.group_id.in_(group_ids), GroupMember.user_id == student_id)
    ).one_or_none()
    return membership is not None


def get_or_create_teacher_group(db: Session, teacher: User) -> Group:
    group = db.scalars(select(Group).where(Group.teacher_id == teacher.id)).first()
    if group is not None:
        return group
    group = Group(name=f"{teacher.username}'s Class", teacher_id=teacher.id)
    db.add(group)
    db.flush()
    return group


def add_student_to_group(db: Session, group_id: uuid.UUID, student_id: uuid.UUID) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=student_id)
    db.add(member)
    db.flush()
    return member
