import base64
import hmac
import time
import typing
import re

import jwt
import sqlalchemy.exc

from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import Headers
from pprint import pprint
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
from utils.date_utils import D

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserToken(BaseModel):
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    user_control_id: Optional[str]
    # disabled: Union[bool, None] = None


# class UserInDB(User):
#     hashed_password: str


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def access_control(request: Request, call_next):
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None
    request.state.user = None
    request.state.service = None

    ip = (
        request.headers["x-forwarded-for"]
        if "x-forwarded-for" in request.headers.keys()
        else request.client.host
    )
    request.state.ip = ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    cookies = request.cookies

    url = request.url.path

    print(f"{url=}")

    try:
        print(2)
        if url.startswith("/login/users/me/"):
            print(3)
            if not auth_exists(request.headers):
                return "no auth"
            print(4)
            if token_ := request.headers.get("authorization") or request.headers.get(
                "Authorization"
            ):
                print(5)
                payload = token_decode(token_)
                username = payload.get("sub", None)
                if username is None:
                    raise credentials_exception
                # token_data -> UserData
                token_data = TokenData(username=username)

                session = next(get_db())  # NOTE:DB 연결해서 사용자 정보 가져오기
                # print(f"{request.state._state=}")

                # request.state.user에 사용자 식별 정보 넘기기
                # request.state.user = UserInDB
                query = f"""
                SELECT USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, USER_CONTROL_ID
                FROM finance.`User`
                WHERE USER_NAME="{token_data.username}"
                """
                result = session.execute(query)
                row = result.fetchone()
                if not row:
                    return False
                USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, USER_CONTROL_ID = row
                request.state.user = UserToken(
                    username=USER_NAME,
                    email=EMAIL,
                    first_name=FIRST_NAME,
                    last_name=LAST_NAME,
                    user_control_id=USER_CONTROL_ID,
                )
                # NOTE: 정보 가져왔으면 session.close() 하기
                session.close()
                # print("asdasdasdadsas")
            else:
                raise credentials_exception
            print(10)
            response = await call_next(request)
            return response
        elif 1:
            print(f"{url=}")
            response = await call_next(request)
            return response
    except Exception as e:
        print(e)
        # Exception 처리하지 못한거 여기서 처리
        # error = await exception_handler(e)
        # error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        # response = JSONResponse(status_code=error.status_code, content=error_dict)
        # await api_logger(request=request, error=error)
        pass
    print(123)
    # return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


def auth_exists(headers: Headers) -> bool:
    if "authorization" in headers.keys() or "Authorization" in headers.keys():
        return True
    return False


def token_style_valid(token: str) -> bool:
    if token.find("Bearer") < 0:
        return False
    try:
        bearer, access_token = token.split()
    except ValueError:
        return False
    return True


def token_decode(access_token: str) -> dict:

    if not token_style_valid(access_token):
        return False

    try:
        _, access_token = access_token.split()
        payload = jwt.decode(access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise credentials_exception
        # raise ex.TokenExpiredEx()
    except DecodeError:
        raise credentials_exception
        # raise ex.TokenDecodeEx()
    return payload
