from fastapi import APIRouter, Depends, Form, HTTPException
import auth
import database
import models_and_schemas
import crud
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
import os


users = APIRouter()


def get_teacherkey():
    if 'TEACHER_KEY' in os.environ:
        return os.environ.get('TEACHER_KEY')
    return os.urandom(24)


@users.post('/registerTeacher')
def register_user(teacherkey: str = Form(), username: str = Form(), full_name: str = Form(), password: str = Form(), db: Session = Depends(database.get_db)):
    if teacherkey != get_teacherkey():
        raise HTTPException(status_code=401, detail="Teacherkey invalid")
    user = models_and_schemas.UserSchema(
        username=username, full_name=full_name, role="teacher", password=password)
    db_user = crud.create_user(db=db, user=user)
    return db_user


@users.post('/registerPupils', dependencies=[Depends(auth.check_teacher)])
def register_pupils(newPupils: models_and_schemas.pupilsList, db: Session = Depends(database.get_db)):
    username_errors = []
    accounts_created = 0
    accounts_received = 0
    for i in newPupils.newPupils:
        if i.fullname == "" or i.username == "" or i.password == "":
            continue
        accounts_received += 1
        pupil = models_and_schemas.UserSchema(
            username=i.username, full_name=i.fullname, role="pupil", password=i.password)

        success = crud.create_user(db=db, user=pupil)
        if success:
            accounts_created += 1
        else:
            username_errors.append(i.username)

    return {'accounts_created': accounts_created, 'username_errors': username_errors, 'accounts_received': accounts_received}


@users.post('/login')
def login(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    if auth.verify_password(form_data.password, db_user.hashed_password):
        token = auth.create_access_token(db_user)
        return {"username": db_user.username, "role": db_user.role, "access_token": token, "token_type": "Bearer"}
    raise HTTPException(status_code=401, detail="Bad username or password")


@users.get('/getAllUsers', dependencies=[Depends(auth.check_teacher)])
def get_users(db: Session = Depends(database.get_db)):
    db_user = crud.get_all_users(db=db)
    return db_user


@users.post('/loggedin', dependencies=[Depends(auth.oauth2_scheme)])
def get_secured(db: Session = Depends(database.get_db)):
    return "secured"


@ users.post('/teacher', dependencies=[Depends(auth.check_teacher)])
def get_teacher(db: Session = Depends(database.get_db)):
    return "teachers only"
