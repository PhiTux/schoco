# see https://www.youtube.com/watch?v=rIC1JEsMzu8

from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime


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
    homeworks: List["Homework"] = Relationship(back_populates="course")


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(unique=True)
    name: str
    description: str
    owner_id: int = Field(foreign_key="user.id")

    owner: "User" = Relationship(back_populates="projects")
    homework: "Homework" = Relationship()


class Homework(SQLModel, table=True):
    id: Optional[int] = Field(default=None, unique=True)
    course_id: int = Field(
        default=None, foreign_key="course.id", primary_key=True)
    project_id: int = Field(
        default=None, foreign_key="project.id", primary_key=True)
    deadline: datetime
    computation_time: int

    course: "Course" = Relationship(back_populates="homeworks")
    orig_project: "Project" = Relationship()


class EditingHomework(SQLModel, table=True):
    project_id: int = Field(
        default=None, foreign_key="project.id", primary_key=True)
    homework_id: int = Field(
        default=None, foreign_key="homework.id", primary_key=True)
    best_submission: Optional[str]
    latest_submission: Optional[str]
    submission_result: Optional[str]
    number_of_compilations: Optional[int]
    number_of_runs: Optional[int]
    number_of_tests: Optional[int]


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


class newProject(BaseModel):
    projectName: str
    projectDescription: str


class updateDescription(BaseModel):
    description: str


class FileChanges(BaseModel):
    path: str
    content: str
    sha: str


class FileChangesList(BaseModel):
    changes: List[FileChanges]


class File(BaseModel):
    path: str
    content: str


class prepareCompile(BaseModel):
    files: List[File]


class startCompile(BaseModel):
    ip: str
    port: int
    container_uuid: str


class startExecute(BaseModel):
    ip: str
    port: int
    container_uuid: str


class startTest(BaseModel):
    ip: str
    port: int
    container_uuid: str
