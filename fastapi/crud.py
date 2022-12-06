from sqlmodel import Session
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


def changePasswordByUsername(username: str, password: str, db: Session):
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
