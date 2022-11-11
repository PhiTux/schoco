from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from fastapi import Request
import database
import users

schoco = FastAPI()

schoco.include_router(users.users)


@schoco.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

schoco.add_middleware(CORSMiddleware, allow_origins=origins,
                      allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@schoco.on_event("startup")
def startup_event():
    database.create_db_and_tables()
