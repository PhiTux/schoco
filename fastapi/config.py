from pydantic import BaseSettings
import os


class Settings(BaseSettings):
    SECRET_KEY: str = os.urandom(24)
    TEACHER_KEY: str = "This is not secure!"
    GITEA_USERNAME: str = "schoco"
    GITEA_PASSWORD: str = "schoco1234"
    GITEA_LOCALHOST_PORT: int = 3000
    GITEA_HOST: str = ""
    MAX_CONTAINERS: int = 8
    PRODUCTION: bool = True
    JWT_EXP_DAYS: int = 15
    FULL_DATA_PATH: str = "/app/data"
    COOKIES_TAG: str = "1.0.0"


settings = Settings()
