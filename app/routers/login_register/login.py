from fastapi import APIRouter, Depends, status, Query, WebSocket, Body

from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt
from enum import Enum
from datetime import datetime, timedelta
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from starlette.requests import Request
from exceptions.auth import *

__all__ = ["router"]

router = APIRouter(prefix="/login")

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    # disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    """
    웹으로부터 받은 비밀번호랑 DB에 있는 해시된 비밀번호 조회
    """
    return plain_password == hashed_password
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    이건 어디에 씀??
    """
    return pwd_context.hash(password)


async def get_user(db: Session, username: str):
    """
    DB에서 사용자 조회
    """
    query = f"""
    SELECT USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, HASHED_PW
    FROM finance.`User`
    WHERE USER_NAME="{username}"
    """
    result = db.execute(query)
    row = result.fetchone()
    if not row:
        return
    USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, HASHED_PW = row
    return UserInDB(
        username=USER_NAME,
        email=EMAIL,
        full_name=f"{FIRST_NAME} {LAST_NAME}",
        hashed_password=HASHED_PW,
    )


async def authenticate_user(db: Session, username: str, password: str):
    """
    DB에 사용자 조회해서 있는지 없는지 확인하는거
    아이디, 비밀번호 불일치하면 그냥 로그인 못하게 만듬 -> ID 있는지 확인하는 꼼수? 못하게
    """
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    로그인하면 시간 제한있는 토큰 만드는 함수
    문자열 JWT 반환함
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    이걸로 로그인 시작 엔드포인트
    """
    # 1. 사용자 아이디&비밀번호 일치 확인
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise CredentialsException(detail="Incorrect username or password")

    # 2. 토큰 만들고 토큰 주기
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    """
        문자열인 JWT 반환하고, 사용자한테  "token_type": "bearer" 이거 반환하라고 함
    """
    return {"access_token": access_token, "token_type": "bearer"}


class UserToken(BaseModel):
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    user_control_id: Optional[str]
