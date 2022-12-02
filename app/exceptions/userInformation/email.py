# -*- coding: utf-8 -*-

from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request

__all__ = ["EmailFormatNotValid", "EmailAlreadyExists"]


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
