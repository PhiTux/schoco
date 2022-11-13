# see https://www.youtube.com/watch?v=rIC1JEsMzu8

from sqlmodel import SQLModel, Field
from enum import Enum
from typing import Optional


class Roles(str, Enum):
    pupil = "pupil"
    teacher = "teacher"


class BaseUser(SQLModel):
    username: str = Field(unique=True)
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""
    role: Roles


class User(BaseUser, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class UserSchema(BaseUser):
    password: str
