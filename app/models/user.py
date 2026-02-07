import uuid
from enum import Enum

from sqlmodel import Field, SQLModel


class UserRole(Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserBase(SQLModel):
    username: str = Field(default="username", unique=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    hashed_password: str | None = Field(default=None)
    role: UserRole = Field(default=UserRole.USER)


class UserPublic(UserBase):
    id: uuid.UUID
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(default="password", min_length=8)
