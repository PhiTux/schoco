from passlib.context import CryptContext
import models_and_schemas
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
import os


pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_secret_key():
    if 'SECRET_KEY' in os.environ:
        return os.environ.get('SECRET_KEY')
    return os.urandom(24)


def get_exp_days():
    if 'JWT_EXP_DAYS' in os.environ:
        return int(os.environ.get('JWT_EXP_DAYS'))
    return 15


def create_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user: models_and_schemas.User):
    claims = {
        "sub": user.username,
        "name": user.full_name,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(days=get_exp_days())
    }
    return jwt.encode(claims=claims, key=get_secret_key(), algorithm="HS256")


def decode_token(token):
    claims = jwt.decode(token, key=get_secret_key())
    return claims


def get_username_by_token(token: str = Depends(oauth2_scheme)):
    claims = jwt.decode(token, key=get_secret_key())
    return claims.get('sub')


def check_teacher(token: str = Depends(oauth2_scheme)):
    claims = decode_token(token)
    role = claims.get('role')
    if role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Only teachers!",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return claims
