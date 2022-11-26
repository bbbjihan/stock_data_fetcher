from fastapi import (
    APIRouter,
    Depends,
    status,
    Query,
    WebSocket,
    Body,
    HTTPException,
    Response,
    Request,
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from urllib import parse
from pprint import pprint
from routers.dep import get_db
from typing import Optional, List, Union, Any
from pydantic import BaseModel, PositiveInt, EmailStr, EmailError, Field, conint, ConstrainedInt
import re
import hashlib
from uuid import uuid4
from datetime import date, datetime

__all__ = ["router"]

router = APIRouter(prefix="/register")

from enum import Enum


class UserName(BaseModel):
    first: str
    last: str


class UserRegisterFrom(BaseModel):
    """
    1. 닉네임
    2. user_control_id
    3. 비밀번호 -> 이건 프론트에서 해시하고 해시값 일치하는지만 검사하면됨
    4. 이름 (first name, lastname)
    5. 나이
    6. 이메일 인증?


    0. 은행계좌 -> 증권사 가입하고 만드는거

    USER_CONTROL_ID는 영원히 바뀌지 않는 값으로
    회원 탈퇴할 때까지 계속 가지고 있는 식별자!!!
    USERNAME, email, first name, last name 바꿔도 절 대 안바뀌는 값임

    """

    username: str = Field(min_length=3, max_length=12)
    hased_pw: str
    user_control_id: str = Field(default_factory=uuid4)
    name: UserName
    email: EmailStr
    birthday: date

    @property
    def valid_age(self):
        today = date.today()
        age = (
            today.year
            - self.birthday.year
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )

        return age > 18

    @property
    def to_sql_insert(self):
        return ",".join(
            [
                f"'{self.username}'",
                f"'{self.user_control_id}'",
                f"'{self.email}'",
                f"'{self.hased_pw}'",
                f"'{self.name.first}'",
                f"'{self.name.last}'",
                f"'{self.birthday}'",
            ]
        )


@router.post("/")
async def register(userRegisterFrom: UserRegisterFrom, db: Session = Depends(get_db)):
    """
    회원 가입하는 엔드포인트
    """
    if not userRegisterFrom.valid_age:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="18세 미만은 가입이 불가능합니다 애송이"
        )

    # print(userRegisterFrom)
    # return 200
    queryy = f"""
    INSERT INTO finance.`User`(USER_NAME, USER_CONTROL_ID,EMAIL, HASHED_PW,  FIRST_NAME, LAST_NAME, BIRTHDAY)
    VALUES ({userRegisterFrom.to_sql_insert})
    """
    db.execute(queryy)
    return 200


def matches_username_policy(usrname: str) -> tuple:

    if len(usrname) < 3 or len(usrname) > 12:
        return (False, "닉네임 길이는 3 이상 12 이하")

    not_allowed = ["섹스", "씨발"]
    pattern2 = re.compile(f"{'|'.join(not_allowed)}")
    not_allowed_words = [x.group() for x in re.finditer(pattern2, usrname)]
    if not_allowed_words:
        return (False, f"{', '.join(not_allowed_words)}는 닉네임에 사용하실 수 없습니다")

    pattern1 = re.compile("^[a-z|A-Z|가-힣|0-9|\-|\_]{3,12}$")
    if pattern1.match(usrname) is None:
        return (False, "닉네임은 영어, 숫자, 한글,'-', '_' 으로만 구성할 수 있습니다")

    return (True, None)


@router.get("/check/username")
async def check_usable_username(able: str, db: Session = Depends(get_db)):
    """
    닉네임 정책, 닉네임 중복 등 확인하는 용도

    /check/username?able=<nickname>
    """

    # 1. 닉네임 정책
    is_able, msg = matches_username_policy(able)
    if not is_able:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=msg)

    # 2. 닉네임 중복 여부 검사
    query = f"""
    SELECT USER_NAME
    FROM finance.User
    WHERE USER_NAME='{able}'
    """
    a = db.execute(query).fetchone()
    if a:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{able} 닉네임은 이미 사용중입니다."
        )

    return Response(content=able, status_code=status.HTTP_202_ACCEPTED)


@router.get("/check/email")
async def check_usable_email(able: str, db: Session = Depends(get_db)):
    """
    이메일 정책, 이메일 중복 확인하는 용도
    """
    # 1. 이메일 형식 검사
    try:
        EmailStr.validate(able)
    except EmailError as ee:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{able}는 옳바른 이메일 형식이 아닙니다"
        )

    # 2. 이메일 중복 여부 검사
    query = f"""
    SELECT EMAIL
    FROM finance.User
    WHERE EMAIL='{able}'
    """
    a = db.execute(query).fetchone()
    if a:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"이미 사용중인 이메일입니다")
    return status.HTTP_200_OK
