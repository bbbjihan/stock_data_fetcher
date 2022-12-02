import time
import re
import jwt
from jwt.exceptions import ExpiredSignatureError, DecodeError
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import Headers
from pprint import pprint
from fastapi import APIRouter, Depends, status, Query, WebSocket, Body
from sqlalchemy.orm import Session
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt
from typing import Union
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from utils.date_utils import D
import exceptions.auth as EAuth
from exceptions.handler import AuthExceptionHandler
from fastapi.logger import logger

"""
    여기 있는 validator는 로그인을 하고나서 사용할 수 있는 API 엔드포인트를 가기전에
    1) 헤더에 토큰이 있는지 확인
    2) 토큰이 유효한지 확인
    3) expire이 안되었는지 확인
    4) 조작된 것이 아닌지 확인
    이런 역할들을 가지고 있다.
    
    뒤에 있는 엔드포인트들이 토큰 해싱하고, 확인하고 이런거 안하게끔 ㅇㅇ
"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 200


def is_endpoint_to_cascade(url: str):

    if url == "/docs":
        return False

    nos = ["/login", "/register"]
    if any([url.startswith(x) for x in nos]):
        return True

    return False


async def access_control(request: Request, call_next):

    url = request.url.path

    if not is_endpoint_to_cascade(url):
        return await call_next(request)

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

    try:
        if url.startswith("/login/users/me/"):
            if not auth_exists(request.headers):
                raise EAuth.CredentialsException
            if token_ := request.headers.get("authorization") or request.headers.get(
                "Authorization"
            ):
                payload = token_decode(token_)
                username = payload.get("sub", None)
                if username is None:
                    # 토큰 안에 sub 이 없을 경우
                    raise EAuth.CredentialsException
                token_data = TokenData(username=username)

                session = next(get_db())  # NOTE:DB 연결해서 사용자 정보 가져오기
                query = f"""
                SELECT USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, USER_CONTROL_ID
                FROM finance.`User`
                WHERE USER_NAME="{token_data.username}"
                """
                result = session.execute(query)
                row = result.fetchone()
                session.close()
                if not row:
                    raise EAuth.UserNotFound
                USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, USER_CONTROL_ID = row
                request.state.user = UserToken(
                    username=USER_NAME,
                    email=EMAIL,
                    first_name=FIRST_NAME,
                    last_name=LAST_NAME,
                    user_control_id=USER_CONTROL_ID,
                )
            else:
                raise EAuth.CredentialsException
            response = await call_next(request)
            return response
        elif 1:
            response = await call_next(request)
            return response
    except EAuth.CredentialsException as error:
        error_dict = dict(detail=error.detail)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
    except EAuth.TokenExceptions as error:
        error_dict = dict(detail=error.detail)
        response = JSONResponse(status_code=error.status_code, content=error.dict)
    except Exception as e:
        # Exception 처리하지 못한거 여기서 처리
        print(e)
    return response


def url_pattern_check(path, pattern):
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
        raise EAuth.TokenMalformed
    try:
        _, access_token = access_token.split()
        payload = jwt.decode(access_token, key=SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise EAuth.TokenExpired
    except DecodeError:
        raise EAuth.TokenDecodeFailed
    return payload
