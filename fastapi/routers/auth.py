from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from os import environ, urandom


auth = APIRouter(prefix="/auth")


class Settings(BaseModel):
    authjwt_secret_key: str = urandom(24)
    if 'SECRET_KEY' in environ:
        authjwt_secret_key: str = environ.get('SECRET_KEY')

    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = True


@AuthJWT.load_config
def get_config():
    return Settings()


@auth.post('/login')
async def login(username: str = "", password: str = "", Authorize: AuthJWT = Depends()):
    print(Authorize.get_raw_jwt())
    if username != 'test' or password != 'test':
        raise HTTPException(
            status_code=401, detail="Bad username or password")

    access_token = Authorize.create_access_token(
        subject=username)
    refresh_token = Authorize.create_refresh_token(
        subject=username)

    Authorize.set_access_cookies(access_token)
    Authorize.set_refresh_cookies(refresh_token)

    return {'Success': True}


@auth.post('/refresh')
def refresh(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()

    subject = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=subject)
    # Set the JWT and CSRF double submit cookies in the response
    Authorize.set_access_cookies(new_access_token)
    return {'Success': True}


@auth.delete('/logout')
def logout(Authorize: AuthJWT = Depends()):
    """
    Because the JWT are stored in an httponly cookie now, we cannot
    log the user out by simply deleting the cookie in the frontend.
    We need the backend to send us a response to delete the cookies.
    """
    Authorize.jwt_required()

    Authorize.unset_jwt_cookies()
    return {'Success': True}
