import uuid

from pydantic import BaseModel

from app.models.user import Role


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    role: Role

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: Role | None = None
