# -*- coding: utf-8 -*-

from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request


@dataclass
class Username:
    @dataclass
    class alreadyExists:
        msg: ClassVar[str] = "username already exists"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE

    @dataclass
    class againstPolicy:
        msg: ClassVar[str] = "Not satisfying username policy"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE


class UsernameAlreadyExists(HTTPException):
    def __init__(self, detail: str = Username.alreadyExists.msg, headers: Mapping[str, str] = None):
        super().__init__(Username.alreadyExists.status_code, detail, headers)


class UsernameAgainstPolicy(HTTPException):
    def __init__(self, detail: str = Username.againstPolicy.msg, headers: Mapping[str, str] = None):
        super().__init__(Username.againstPolicy.status_code, detail, headers)


@dataclass
class Email:
    @dataclass
    class malformed:
        msg: ClassVar[str] = "Not valid E-mail format"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE

    @dataclass
    class alreadyExists:
        msg: ClassVar[str] = "E-mail already exists"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE


class EmailFormatNotValid(HTTPException):
    def __init__(self, detail: str = Email.malformed.msg, headers: Mapping[str, str] = None):
        super().__init__(Email.malformed.status_code, detail, headers)


class EmailAlreadyExists(HTTPException):
    def __init__(self, detail: str = Email.alreadyExists.msg, headers: Mapping[str, str] = None):
        super().__init__(Email.alreadyExists.status_code, detail, headers)


@dataclass
class UserAge:
    @dataclass
    class notAcceptable:
        msg: ClassVar[str] = "18세 미만은 가입이 불가능합니다 애송이"
        status_code: ClassVar[int] = status.HTTP_406_NOT_ACCEPTABLE


class TooYoung(HTTPException):
    def __init__(self, detail: str = UserAge.notAcceptable.msg, headers: Mapping[str, str] = None):
        super().__init__(UserAge.notAcceptable.status_code, detail, headers)
