from fastapi import APIRouter, Depends, HTTPException
import auth
import database
import models_and_schemas
import crud
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm


users = APIRouter()


@users.post('/register')
def register_user(user: models_and_schemas.UserSchema, db: Session = Depends(database.get_db)):
    db_user = crud.create_user(db=db, user=user)
    return db_user


@users.post('/login')
def login(db: Session = Depends(database.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # def login(username: str = "", password: str = "", db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_username(db=db, username=form_data.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Bad username or password")
    if auth.verify_password(form_data.password, db_user.hashed_password):
        token = auth.create_access_token(db_user)
        return {"access_token": token, "token_type": "Bearer"}
    raise HTTPException(status_code=401, detail="Bad username or password")


@users.get('/users')
def get_users(db: Session = Depends(database.get_db)):
    db_user = crud.get_all_users(db=db)
    return db_user


@users.post('/secured')
def get_secured(db: Session = Depends(database.get_db), token: str = Depends(auth.oauth2_scheme)):
    return "secured"
