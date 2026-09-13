import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import Role, User
from app.repositories import user_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_access_token(token)
    if payload is None:
        raise _credentials_exception

    raw_user_id = payload.get("sub")
    if raw_user_id is None:
        raise _credentials_exception
    try:
        user_id = uuid.UUID(raw_user_id)
    except ValueError:
        raise _credentials_exception

    user = user_repository.get_by_id(db, user_id)
    if user is None:
        raise _credentials_exception
    return user


def require_roles(*allowed_roles: Role) -> Callable[[User], User]:
    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action",
            )
        return current_user

    return checker


require_teacher = require_roles(Role.TEACHER)
require_student = require_roles(Role.STUDENT)
require_staff = require_roles(Role.TEACHER)
