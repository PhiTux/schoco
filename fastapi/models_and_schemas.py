from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel

# alembic readme:
"""
When updating the database models, you need to create a new revision with Alembic.
BEFORE creating the model, make sure, that your old DB has included the metadata of the old alembic-revision.
-> call: alembic -c alembic_dev.ini upgrade head

Then edit the models and create a new revision:
-> call: alembic -c alembic_dev.ini revision --autogenerate -m "EXCPLAIN WHAT YOU CHANGED"

Afterwards actually update the dev-database:
-> call: alembic -c alembic_dev.ini upgrade head
"""

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
    must_change_password: Optional[bool] = False

    courses: List["Course"] = Relationship(
        back_populates="users", link_model=UserCourseLink)

    projects: List["Project"] = Relationship(back_populates="owner")

    homeworks: List["EditingHomework"] = Relationship(back_populates="owner")


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
    computation_time: Optional[int] = 10
    main_class: str

    owner: "User" = Relationship(back_populates="projects")


class Homework(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course_id: int = Field(
        default=None, foreign_key="course.id")
    template_project_id: int = Field(
        default=None, foreign_key="project.id", unique=True)
    original_project_id: int = Field(
        default=None, foreign_key="project.id")
    deadline: str  # datetime
    solution_project_id: Optional[int] = Field(
        default=None, foreign_key="project.id")
    # datetime, when the solution may be shown to pupils
    solution_start_showing: Optional[str] = ""
    enable_tests: Optional[bool] = True

    course: "Course" = Relationship(back_populates="homeworks")


class EditingHomework(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # uuid: str = Field(unique=True) -> get uuid from howework->template-project
    homework_id: int = Field(
        default=None, foreign_key="homework.id")
    owner_id: int = Field(
        default=None, foreign_key="user.id")  # owner_id = branch_name

    submission: Optional[str] = ""
    # submission having the structure {passed_tests: ..., failed_tests: ...}

    number_of_compilations: Optional[int] = 0
    number_of_runs: Optional[int] = 0
    number_of_tests: Optional[int] = 0

    owner: "User" = Relationship()
    homework: "Homework" = Relationship()

# other models


class newPupil(BaseModel):
    fullname: str
    username: str
    password: str


class pupilsList(BaseModel):
    newPupils: List[newPupil]
    courseIDs: List[int]


class setPassword(BaseModel):
    username: str
    password: str


class AddUserCourseLink(BaseModel):
    user_id: int
    coursename: str


class UserById(BaseModel):
    user_id: int


class changeName(BaseModel):
    user_id: int
    name: str


class newProject(BaseModel):
    projectName: str
    className: str
    projectDescription: str
    language: str


class updateText(BaseModel):
    text: str


class FileChanges(BaseModel):
    path: str
    content: str
    sha: str


class FileChangesList(BaseModel):
    changes: List[FileChanges]


class File(BaseModel):
    path: str
    content: str


class filesList(BaseModel):
    files: List[File]


class startCompile(BaseModel):
    port: int
    container_uuid: str
    save_output: bool


class startExecute(BaseModel):
    port: int
    container_uuid: str
    save_output: bool


class startTest(BaseModel):
    port: int
    container_uuid: str


class create_homework(BaseModel):
    files: List[File]
    course_id: int
    deadline_date: str
    computation_time: int
    enable_tests: bool


class homeworkId(BaseModel):
    id: int


class courseID(BaseModel):
    id: int


class RenameFile(BaseModel):
    old_path: str
    new_path: str
    content: str
    sha: str


class RenameHomework(BaseModel):
    id: int
    new_name: str


class ChangePassword(BaseModel):
    oldPassword: str
    newPassword: str


class AddClass(BaseModel):
    className: str
    language: str


class DeleteFile(BaseModel):
    path: str
    sha: str


class UpdateHomeworkSettings(BaseModel):
    id: int
    deadline_date: str
    computation_time: int
    enable_tests: bool


class UUID(BaseModel):
    uuid: str


class Password(BaseModel):
    password: str


class AddSolution(BaseModel):
    homework_id: int
    solution_id: int
    solution_start_showing: str


class DeleteSolution(BaseModel):
    homework_id: int


class EntryPoint(BaseModel):
    entry_point: str


class SkipVersion(BaseModel):
    skip_version: str


class ComputationTime(BaseModel):
    computation_time: int
