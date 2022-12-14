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
from datetime import date
from exceptions.userInformation import *

__all__ = ["router"]

router = APIRouter(prefix="/update")

from enum import Enum


class UserName(BaseModel):
    first: Optional[str]
    last: Optional[str]


class UserDataModify(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=12)
    hased_pw: Optional[str]
    name: Optional[UserName]
    email: Optional[EmailStr]
    birthday: Optional[date]

    @property
    def valid_age(self):
        if not self.birthday:
            return True
        today = date.today()
        age = (
            today.year
            - self.birthday.year
            - ((today.month, today.day) < (self.birthday.month, self.birthday.day))
        )

        return age > 18

    def filled(self):
        return any(list(self.dict().values()))


class UserUpdateForm(BaseModel):
    username: str = Field(min_length=3, max_length=12)
    hased_pw: str
    new: UserDataModify

    @property
    def is_valid_request(self):
        if not self.new.filled():
            return False
        return True

    def to_sql_update(self, o_usrname, o_email, o_fst_name, o_last_name, o_bday):
        def quic(col, val):
            return f'{col}="{val}"' if val else ""

        set_queries = []
        set_queries.append(quic("USER_NAME", self.new.username))
        set_queries.append(quic("EMAIL", self.new.email))
        set_queries.append(quic("FIRST_NAME", self.new.name and self.new.name.first))
        set_queries.append(quic("LAST_NAME", self.new.name and self.new.name.last))
        set_queries.append(
            quic("BIRTHDAY", self.new.birthday and self.new.birthday.strftime("%Y-%m-%d"))
        )
        set_queries = [x for x in set_queries if x]
        return ",".join(set_queries)


@router.put("/")
async def udpate_user_info(userUpdateForm: UserUpdateForm, db: Session = Depends(get_db)):
    """
    ?????? ???????????? ???????????????
    ??? ????????? ?????? ?????? ID??? ????????? ??? ????????? ?????? ??? ??????
    """
    # print(userUpdateForm)
    # 0. ??????????????? ??? ???????????? ??????
    if not userUpdateForm.is_valid_request:
        raise TooYoung()

    # 1. ?????? ????????? ???????????? ??????
    queryy = f"""
    SELECT USER_NAME, EMAIL, USER_CONTROL_ID, FIRST_NAME, LAST_NAME, BIRTHDAY
    FROM finance.`User`
    WHERE 
        USER_NAME='{userUpdateForm.username}' AND
        HASHED_PW='{userUpdateForm.hased_pw}'
    """
    a = db.execute(queryy).fetchone()

    if not a:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="??????????????? ???????????? ????????????")
    USER_NAME, EMAIL, USER_CONTROL_ID, FIRST_NAME, LAST_NAME, BIRTHDAY = a

    # 2. ?????? ????????? ?????? ?????? -> ????????? ????????? ????????? ????????? ?????? ??????????????? ??????;
    if not userUpdateForm.new.valid_age:
        raise TooYoung()

    # 3. ???????????? - ! ????????? ?????? ?????? ?????? ?????????

    set_query = userUpdateForm.to_sql_update(USER_NAME, EMAIL, FIRST_NAME, LAST_NAME, BIRTHDAY)
    # print(f"NEW : {set_query}")

    queryy = f"""
    UPDATE finance.`User`
    SET {set_query}
    WHERE USER_CONTROL_ID="{USER_CONTROL_ID}"
    """
    # pprint(queryy)
    db.execute(queryy)
    return 200
