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
    teacherkey: str = os.urandom(24)
    if 'TEACHER_KEY' in os.environ:
        teacherkey: str = os.environ.get('TEACHER_KEY')
    return teacherkey


@users.post('/registerTeacher')
def register_user(teacherkey: str = Form(), username: str = Form(), first_name: str = Form(), last_name: str = Form(), password: str = Form(), db: Session = Depends(database.get_db)):
    if teacherkey != get_teacherkey():
        raise HTTPException(status_code=401, detail="Teacherkey invalid")
    user = models_and_schemas.UserSchema(
        username=username, first_name=first_name, last_name=last_name, role="teacher", password=password)
    db_user = crud.create_user(db=db, user=user)
    return db_user


@users.post('/login')
def login(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    if auth.verify_password(form_data.password, db_user.hashed_password):
        token = auth.create_access_token(db_user)
        return {"username": db_user.username, "role": db_user.role, "access_token": token, "token_type": "Bearer"}
    raise HTTPException(status_code=401, detail="Bad username or password")


@users.get('/users')
def get_users(db: Session = Depends(database.get_db)):
    db_user = crud.get_all_users(db=db)
    return db_user


@users.post('/loggedin', dependencies=[Depends(auth.oauth2_scheme)])
def get_secured(db: Session = Depends(database.get_db)):
    return "secured"


@ users.post('/teacher', dependencies=[Depends(auth.check_teacher)])
def get_teacher(db: Session = Depends(database.get_db)):
    return "teachers only"
