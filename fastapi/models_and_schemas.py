# see https://www.youtube.com/watch?v=rIC1JEsMzu8

from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


# database models
class PupilCourseLink(SQLModel, table=True):
    user_id: Optional[int] = Field(
        default=None, foreign_key="user.id", primary_key=True)
    course_id: Optional[int] = Field(
        default=None, foreign_key="course.id", primary_key=True)


class Roles(str, Enum):
    pupil = "pupil"
    teacher = "teacher"


class BaseUser(SQLModel):
    username: str = Field(unique=True)
    full_name: str
    role: Roles


class User(BaseUser, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    courses: List["Course"] = Relationship(
        back_populates="pupils", link_model=PupilCourseLink)


class UserSchema(BaseUser):
    password: str


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    color: str
    fontDark: bool

    pupils: List["User"] = Relationship(
        back_populates="courses", link_model=PupilCourseLink)


# other models

class newPupil(BaseModel):
    fullname: str
    username: str
    password: str


class pupilsList(BaseModel):
    newPupils: List[newPupil]


class setPassword(BaseModel):
    username: str
    password: str
