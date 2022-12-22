# see https://www.youtube.com/watch?v=rIC1JEsMzu8

from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


# database models
class UserCourseLink(SQLModel, table=True):
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
        back_populates="users", link_model=UserCourseLink)

    projects: List["Project"] = Relationship(back_populates="owner")


class UserSchema(BaseUser):
    password: str


class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    color: str
    fontDark: bool

    users: List["User"] = Relationship(
        back_populates="courses", link_model=UserCourseLink)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True)
    name: str
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="projects")


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


class AddUserCourseLink(BaseModel):
    user_id: int
    coursename: str


class UserById(BaseModel):
    user_id: int


class ProjectName(BaseModel):
    projectName: str


class ProjectUuid(BaseModel):
    project_uuid: str
