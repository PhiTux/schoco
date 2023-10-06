import re
import requests
from fastapi import APIRouter, Depends, Form, HTTPException
import auth
import database_config
import models_and_schemas
import crud
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from config import settings
import json
from datetime import datetime, timedelta


if settings.PRODUCTION:
    UPDATE_NOTIFICATION_FILE = "/app/data/update_notification.json"
else:
    UPDATE_NOTIFICATION_FILE = "./data/update_notification.json"


users = APIRouter(prefix="/api")


@users.post('/registerTeacher')
def register_user(teacherkey: str = Form(), username: str = Form(), full_name: str = Form(), password: str = Form(), db: Session = Depends(database_config.get_db)):
    if teacherkey != settings.TEACHER_KEY:
        raise HTTPException(status_code=401, detail="Teacherkey invalid")
    if username.strip() == "" or " " in username.strip():
        raise HTTPException(status_code=400, detail="Username invalid")
    if full_name.strip() == "":
        raise HTTPException(status_code=400, detail="Fullname empty")
    if not check_password_criteria(password):
        raise HTTPException(status_code=400, detail="Password invalid")
    user = models_and_schemas.UserSchema(
        username=username, full_name=full_name, role="teacher", password=password)
    db_user = crud.create_user(db=db, user=user)
    return db_user


@users.post('/registerPupils', dependencies=[Depends(auth.check_teacher)])
def register_pupils(newPupils: models_and_schemas.pupilsList, db: Session = Depends(database_config.get_db)):
    username_errors = []
    accounts_created = 0
    accounts_received = 0
    course_error = False
    for i in newPupils.newPupils:
        if i.fullname.strip() == "" and i.username.strip() == "" and i.password.strip() == "":
            continue
        elif i.fullname.strip() == "" or i.username.strip() == "" or " " in i.username.strip() or not check_password_criteria(i.password):
            accounts_received += 1
            username_errors.append(i.fullname + " (" + i.username + ")")
            continue
        accounts_received += 1
        pupil = models_and_schemas.UserSchema(
            username=i.username.strip(), full_name=i.fullname.strip(), role="pupil", password=i.password)

        success = crud.create_user(db=db, user=pupil)
        if success:
            accounts_created += 1
        else:
            username_errors.append(i.fullname + " (" + i.username + ")")

        user = crud.get_user_by_username(db=db, username=i.username.strip())
        for c in newPupils.courseIDs:
            courseUserLink = models_and_schemas.UserCourseLink(
                user_id=user.id, course_id=c)
            if not crud.create_UserCourseLink(db=db, link=courseUserLink):
                course_error = True

    return {'accounts_created': accounts_created, 'username_errors': username_errors, 'accounts_received': accounts_received, 'course_error': course_error}


def check_password_criteria(password: str):
    if len(password) < 8:
        return False

    # must fulfill at least 2 of the following 3 criteria
    criteria_fulfilled = 0
    # check if password contains at least one number
    for i in password:
        if i.isdigit():
            criteria_fulfilled += 1
            break

    # check if password contains at least one letter
    for i in password:
        if i.isalpha():
            criteria_fulfilled += 1
            break

    # check if password contains at least one special character
    for i in password:
        if not i.isdigit() and not i.isalpha():
            criteria_fulfilled += 1
            break

    if criteria_fulfilled >= 2:
        return True

    return False


@users.post('/setNewPassword', dependencies=[Depends(auth.check_teacher)])
async def setNewPassword(setPassword: models_and_schemas.setPassword, db: Session = Depends(database_config.get_db)):
    if not check_password_criteria(setPassword.password):
        raise HTTPException(
            status_code=400, detail="Password invalid")
    if not crud.change_password_by_username(setPassword.username, setPassword.password, db):
        raise HTTPException(
            status_code=500, detail="Password change not successful")
    return {'success': True}


@users.post('/changePassword', dependencies=[Depends(auth.oauth2_scheme)])
async def changePassword(changePassword: models_and_schemas.ChangePassword, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    db_user = crud.get_user_by_username(db=db, username=username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    if not auth.verify_password(changePassword.oldPassword, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Bad username or password")

    if not check_password_criteria(changePassword.newPassword):
        raise HTTPException(status_code=401, detail="Bad username or password")

    if not crud.change_password_by_username(username=username, password=changePassword.newPassword, db=db):
        raise HTTPException(
            status_code=500, detail="Password change not successful")

    return {'success': True}


@users.post('/addNewCourse', dependencies=[Depends(auth.check_teacher)])
async def addNewCourse(newCourse: models_and_schemas.Course, db: Session = Depends(database_config.get_db)):
    if len(newCourse.name) < 2 or len(newCourse.name) > 30:
        raise HTTPException(
            status_code=403, detail="Course name length must be between 2 to 30.")
    success = crud.create_course(db=db, course=newCourse)
    if not success:
        raise HTTPException(
            status_code=500, detail="Course creation not successful")

    return {'success': True}


@users.post('/editCourse', dependencies=[Depends(auth.check_teacher)])
async def editCourse(editCourse: models_and_schemas.Course, db: Session = Depends(database_config.get_db)):
    if len(editCourse.name) < 2 or len(editCourse.name) > 30:
        raise HTTPException(
            status_code=403, detail="Course name length must be between 2 to 30.")
    if not crud.edit_course(db=db, course=editCourse):
        raise HTTPException(
            status_code=500, detail="Course edit not successful")

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
    if changeName.name.strip() == "":
        return False
    return crud.change_name(db=db, user_id=changeName.user_id, name=changeName.name.strip())


@users.post('/changeUsername', dependencies=[Depends(auth.check_teacher)])
def change_username(changeName: models_and_schemas.changeName, db: Session = Depends(database_config.get_db)):
    if changeName.name.strip() == "" or " " in changeName.name.strip():
        return False
    last_username = crud.change_username(
        db=db, user_id=changeName.user_id, name=changeName.name.strip())
    return {'last_username': last_username}


@users.post('/checkExistingHomework', dependencies=[Depends(auth.check_teacher)])
def checkExistingHomework(uuid: models_and_schemas.UUID, db: Session = Depends(database_config.get_db)):
    project = crud.get_project_by_project_uuid(db=db, project_uuid=uuid.uuid)

    homeworkCourses = crud.get_courses_of_homework_by_original_uuid(
        db=db, original_project_id=project.id)

    return homeworkCourses


@users.post('/confirmTeacherPassword', dependencies=[Depends(auth.check_teacher)])
def confirmTeacherPassword(password: models_and_schemas.Password, db: Session = Depends(database_config.get_db), username=Depends(auth.get_username_by_token)):
    user = crud.get_user_by_username(db=db, username=username)

    if auth.verify_password(password.password, user.hashed_password):
        return {'success': True}

    return {'success': False}


def major_minor_micro(version):
    major, minor, micro = re.search('(\d+)\.(\d+)\.(\d+)', version).groups()

    return int(major), int(minor), int(micro)


def docker_api_get_latest_version():
    r = requests.get(
        'https://hub.docker.com/v2/repositories/phitux/schoco-frontend/tags')
    r = r.json()
    versions = [v['name'] for v in r['results'] if v['name']
                != 'latest' and v['name'].count('.') == 2]

    return max(versions, key=major_minor_micro)


@users.get('/getLatestVersion', dependencies=[Depends(auth.check_teacher)])
def get_latest_version():
    '''
    {
        "latest_version": "1.0.0",
        "last_update": "2021-08-01 12:00:00",
        "skip_version": "0.0.0"
    }
    '''

    latest_version = ""
    last_update = ""
    skip_version = "0.0.0"

    # check if json file exists
    try:
        with open(UPDATE_NOTIFICATION_FILE) as f:
            data = json.load(f)
            if 'latest_version' in data:
                latest_version = data.get('latest_version')
            if 'last_update' in data:
                last_update = data.get('last_update')
            if 'skip_version' in data:
                skip_version = data.get('skip_version')
    except:
        print("no json file found")

    # check if data needs to be updated

    # if last_update is older than 1h...
    if last_update == "" or datetime.fromisoformat(last_update) < datetime.now() - timedelta(hours=1):
        latest_version = docker_api_get_latest_version()

        # save
        with open(UPDATE_NOTIFICATION_FILE, 'w') as f:
            json.dump({'latest_version': latest_version,
                       'last_update': str(datetime.now().isoformat()),
                       'skip_version': skip_version}, f)

    # check if version is to be skipped
    if latest_version == skip_version:
        return {"skip_version": latest_version, "latest_version": latest_version}

    # return
    return {"skip_version": skip_version, "latest_version": latest_version}


@users.post('/skipLatestVersion', dependencies=[Depends(auth.check_teacher)])
def skip_latest_version(skip_version: models_and_schemas.SkipVersion):
    # read json
    try:
        with open(UPDATE_NOTIFICATION_FILE) as f:
            data = json.load(f)
            if 'latest_version' in data:
                latest_version = data.get('latest_version')
            if 'last_update' in data:
                last_update = data.get('last_update')
    except:
        return {"success": False}

    with open(UPDATE_NOTIFICATION_FILE, 'w') as f:
        json.dump({'latest_version': latest_version,
                   'last_update': last_update,
                   'skip_version': skip_version.skip_version}, f)

    return {"success": True}
