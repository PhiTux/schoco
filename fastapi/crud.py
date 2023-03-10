from sqlmodel import Session, select
from sqlalchemy import exc
import auth
import models_and_schemas


def create_user(db: Session, user: models_and_schemas.UserSchema):
    hashed_password = auth.create_password_hash(user.password)
    db_user = models_and_schemas.User(
        username=user.username,
        full_name=user.full_name,
        role=user.role,
        hashed_password=hashed_password
    )
    try:
        db.add(db_user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def create_course(db: Session, course: models_and_schemas.Course):
    try:
        db.add(course)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_course_by_coursename(db: Session, coursename: str):
    course = db.query(models_and_schemas.Course).filter(
        models_and_schemas.Course.name == coursename).first()
    return course


def get_course_by_id(db: Session, id: int):
    course = db.query(models_and_schemas.Course).filter(
        models_and_schemas.Course.id == id).first()
    return course


def get_user_by_username(db: Session, username: str):
    user = db.query(models_and_schemas.User).filter(
        models_and_schemas.User.username == username).first()
    return user


def get_user_by_id(db: Session, id: int):
    user = db.query(models_and_schemas.User).filter(
        models_and_schemas.User.id == id).first()
    return user


def change_password_by_username(username: str, password: str, db: Session):
    try:
        db.query(models_and_schemas.User).filter(models_and_schemas.User.username ==
                                                 username).update({'hashed_password': auth.create_password_hash(password)})
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_all_users(db: Session):
    users = db.query(models_and_schemas.User).all()
    return users


def get_all_courses(db: Session):
    courses = db.query(models_and_schemas.Course).all()
    return courses


def create_UserCourseLink(db: Session, link: models_and_schemas.UserCourseLink):
    try:
        db.add(link)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def get_user_course_link(db: Session, link: models_and_schemas.UserCourseLink):
    link = db.query(models_and_schemas.UserCourseLink).filter(models_and_schemas.UserCourseLink.course_id ==
                                                              link.course_id, models_and_schemas.UserCourseLink.user_id == link.user_id).first()
    return link


def remove_UserCourseLink(db: Session, link: models_and_schemas.UserCourseLink):
    try:
        db.delete(link)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def remove_user(db: Session, user: models_and_schemas.User):
    try:
        db.delete(user)
        db.commit()
    except:
        db.rollback()
        return False
    return True


def create_project(db: Session, project: models_and_schemas.Project):
    try:
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_project_by_project_uuid(db: Session, project_uuid: str):
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.uuid == project_uuid)).first()
    return project


def get_project_by_id(db: Session, id: int):
    project = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.id == id)).first()
    return project


def get_projects_by_ids(db: Session, ids: list[int]):
    return db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.id.in_(ids))).all()


def get_projects_by_username(db: Session, username: str):
    owner = db.exec(select(models_and_schemas.User).where(
        models_and_schemas.User.username == username)).first()
    projects = db.exec(select(models_and_schemas.Project).where(
        models_and_schemas.Project.owner == owner)).all()
    return projects


def update_description(db: Session, project_uuid: str, description: str):
    try:
        project = db.exec(select(models_and_schemas.Project).where(
            models_and_schemas.Project.uuid == project_uuid)).first()
        project.description = description
        db.add(project)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def create_homework(db: Session, homework: models_and_schemas.Homework):
    try:
        db.add(homework)
        db.commit()
    except Exception as e:
        print(e)
        db.rollback()
        return False
    return True


def get_homework_by_username(db: Session, username: str):
    """return all homework, that was created (!) by given username"""
    # get my project_ids
    project_ids = db.exec(select(models_and_schemas.Project.id).join(
        models_and_schemas.User).where(models_and_schemas.User.username == username)).all()
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.original_project_id.in_(project_ids))).all()
    return homework


def get_courses_by_username(db: Session, username: str):
    user = db.exec(select(models_and_schemas.User).where(
        models_and_schemas.User.username == username)).first()
    return user.courses


def get_homework_by_courses(db: Session, courses: list[models_and_schemas.Course]):
    courses_ids = []
    for c in courses:
        courses_ids.append(c.id)
    homework = db.exec(select(models_and_schemas.Homework).where(
        models_and_schemas.Homework.course_id.in_(courses_ids))).all()
    return homework


def get_editing_homework_by_username(db: Session, username: str):
    user = get_user_by_username(db, username)
    editing_homework = db.exec(select(models_and_schemas.EditingHomework).where(
        models_and_schemas.EditingHomework.owner == user)).all()
    return editing_homework
