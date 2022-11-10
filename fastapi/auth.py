from passlib.context import CryptContext
import models_and_schemas
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import os


pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_secret_key():
    authjwt_secret_key: str = os.urandom(24)
    if 'SECRET_KEY' in os.environ:
        authjwt_secret_key: str = os.environ.get('SECRET_KEY')
    return authjwt_secret_key


def get_exp_days():
    authjwt_exp = 15
    if 'JWT_EXP_DAYS' in os.environ:
        authjwt_exp = int(os.environ.get('JWT_EXP_DAYS'))
    return authjwt_exp


def create_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user: models_and_schemas.User):
    claims = {
        "sub": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(days=get_exp_days())
    }
    return jwt.encode(claims=claims, key=get_secret_key(), algorithm="HS256")
