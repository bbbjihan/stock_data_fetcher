import pathlib
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from typing import List, Optional, Union
from os import environ
from dotenv import load_dotenv

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=f"{ROOT}/.env")


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    "mysql+pymysql://root:mwnsgud1!@localhost/finance"
    MYSQL_DATABASE_URI: Optional[str] = "{}://{}:{}@{}:{}/{}".format(
        environ.get("DB_TYPE"),
        environ.get("DB_USER"),
        environ.get("DB_PASSWD"),
        environ.get("DB_HOST"),
        environ.get("DB_PORT"),
        environ.get("DB_NAME"),
    )
    # environ.get("DB_NAME"),
    MYSQL_DATABASE_HOST: Optional[str] = environ.get("DB_HOST")
    MYSQL_DATABASE_PORT: Optional[int] = environ.get("DB_PORT")
    # FIRST_SUPERUSER: EmailStr = "admin@recipeapi.com"

    class Config:
        case_sensitive = True


settings = Settings()
