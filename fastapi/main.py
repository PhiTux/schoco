from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from multiprocessing import Lock
import database_config
import users
import code
import cookies_api
from fastapi_utils.tasks import repeat_every
""" from fastapi.logger import logger
import logging

gunicorn_logger = logging.getLogger('gunicorn.error')
logger.handlers = gunicorn_logger.handlers
if __name__ != "main":
    logger.setLevel(gunicorn_logger.level)
else:
    logger.setLevel(logging.DEBUG) """


app = FastAPI()

app.include_router(users.users)
app.include_router(code.code)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(CORSMiddleware, allow_origins=origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


lock = Lock()
firstRun = True


@app.on_event("startup")
@repeat_every(seconds=60)
def startup_event():
    global firstRun
    if firstRun:
        database_config.create_db_and_tables()
        firstRun = False
        with lock:
            cookies_api.fillNewContainersQueue()
    else:
        with lock:
            cookies_api.refillNewContainersQueue()
