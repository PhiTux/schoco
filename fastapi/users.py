from fastapi import APIRouter, Depends, Form, HTTPException, Body, Request
import auth
import database_config
import models_and_schemas
import crud
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from config import settings


users = APIRouter(prefix="/api")


@users.post('/registerTeacher')
def register_user(teacherkey: str = Form(), username: str = Form(), full_name: str = Form(), password: str = Form(), db: Session = Depends(database_config.get_db)):
    if teacherkey != settings.TEACHER_KEY:
        raise HTTPException(status_code=401, detail="Teacherkey invalid")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")
    user = models_and_schemas.UserSchema(
        username=username, full_name=full_name, role="teacher", password=password)
    db_user = crud.create_user(db=db, user=user)
    return db_user


@users.post('/registerPupils', dependencies=[Depends(auth.check_teacher)])
def register_pupils(newPupils: models_and_schemas.pupilsList, db: Session = Depends(database_config.get_db)):
    username_errors = []
    accounts_created = 0
    accounts_received = 0
    for i in newPupils.newPupils:
        if i.fullname == "" and i.username == "" and i.password == "":
            continue
        elif i.fullname == "" or i.username == "" or len(i.password) < 8:
            accounts_received += 1
            username_errors.append(i.fullname + " (" + i.username + ")")
        accounts_received += 1
        pupil = models_and_schemas.UserSchema(
            username=i.username, full_name=i.fullname, role="pupil", password=i.password)

        success = crud.create_user(db=db, user=pupil)
        if success:
            accounts_created += 1
        else:
            username_errors.append(i.fullname + " (" + i.username + ")")

    return {'accounts_created': accounts_created, 'username_errors': username_errors, 'accounts_received': accounts_received}


@users.post('/setNewPassword', dependencies=[Depends(auth.check_teacher)])
async def setNewPassword(setPassword: models_and_schemas.setPassword, db: Session = Depends(database_config.get_db)):
    if not crud.change_password_by_username(setPassword.username, setPassword.password, db):
        raise HTTPException(
            status_code=500, detail="Password change not successful")
    return {'success': True}


@users.post('/addNewCourse', dependencies=[Depends(auth.check_teacher)])
async def addNewCourse(newCourse: models_and_schemas.Course, db: Session = Depends(database_config.get_db)):
    success = crud.create_course(db=db, course=newCourse)
    if not success:
        raise HTTPException(
            status_code=500, detail="Course creation not successful")

    return {'success': True}


@users.post('/removeCourse', dependencies=[Depends(auth.check_teacher)])
def removeCourse(courseId: models_and_schemas.courseID, db: Session = Depends(database_config.get_db)):

    # remove course and associated homework, editingHomework, template-projects and user-course-links
    if not crud.remove_course(db=db, course_id=courseId.id):
        raise HTTPException(
            status_code=500, detail="Course deletion not successful")

    return {'success': True}


@users.post('/addCourseToUser', dependencies=[Depends(auth.check_teacher)])
def addCourseToUser(addUserCourseLink: models_and_schemas.AddUserCourseLink, db: Session = Depends(database_config.get_db)):
    course = crud.get_course_by_coursename(
        db=db, coursename=addUserCourseLink.coursename)
    courseUserLink = models_and_schemas.UserCourseLink(
        user_id=addUserCourseLink.user_id, course_id=course.id)
    if not crud.create_UserCourseLink(db=db, link=courseUserLink):
        raise HTTPException(
            status_code=500, detail="Could not link Course to User")

    return {'success': True}


@users.post('/removeCourseFromUser', dependencies=[Depends(auth.check_teacher)])
def removeCourseFromUser(userCourseLink: models_and_schemas.UserCourseLink, db: Session = Depends(database_config.get_db)):
    link = crud.get_user_course_link(db=db, link=userCourseLink)
    if not crud.remove_UserCourseLink(db=db, link=link):
        raise HTTPException(
            status_code=500, detail="Could not remove Course from User")

    return {'success': True}


@users.post('/deleteUser', dependencies=[Depends(auth.check_teacher)])
def delete_user(userById: models_and_schemas.UserById, db: Session = Depends(database_config.get_db)):
    db_user = db.get(models_and_schemas.User, userById.user_id)
    if not crud.remove_user(db=db, user=db_user):
        return {'success': False}
    return {'success': True}


@users.post('/login')
def login(db: Session = Depends(database_config.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    if auth.verify_password(form_data.password, db_user.hashed_password):
        token = auth.create_access_token(db_user)
        return {"username": db_user.username, "role": db_user.role, "access_token": token, "token_type": "Bearer"}
    raise HTTPException(status_code=401, detail="Bad username or password")


@users.get('/getAllUsers', dependencies=[Depends(auth.check_teacher)])
def get_users(db: Session = Depends(database_config.get_db)):
    db_user = crud.get_all_users(db=db)
    coursesList = []
    for u in db_user:
        coursesList.append({'user_id': u.id, 'courses': u.courses})
    return {'users': db_user, 'coursesList': coursesList}


@users.get('/getAllCourses', dependencies=[Depends(auth.check_teacher)])
def get_courses(db: Session = Depends(database_config.get_db)):
    courses = crud.get_all_courses(db=db)
    return courses


@users.post('/changeName', dependencies=[Depends(auth.check_teacher)])
def change_name(changeName: models_and_schemas.changeName, db: Session = Depends(database_config.get_db)):
    return crud.change_name(db=db, user_id=changeName.user_id, name=changeName.name.strip())


@users.post('/changeUsername', dependencies=[Depends(auth.check_teacher)])
def change_username(changeName: models_and_schemas.changeName, db: Session = Depends(database_config.get_db)):
    return crud.change_username(db=db, user_id=changeName.user_id, name=changeName.name.strip())
