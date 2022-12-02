from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request


@dataclass
class RequestBody:
    @dataclass
    class notEnough:
        msg: ClassVar[str] = "not enough request body data"
        status_code: ClassVar[int] = status.HTTP_422_UNPROCESSABLE_ENTITY

    @dataclass
    class empty:
        msg: ClassVar[str] = "empty request body"
        status_code: ClassVar[int] = status.HTTP_422_UNPROCESSABLE_ENTITY


class NotEnoughRequestBody(HTTPException):
    def __init__(
        self,
        status_code: int = RequestBody.notEnough.status_code,
        detail: str = RequestBody.notEnough.msg,
        headers: Mapping[str, str] = None,
    ):
        super().__init__(status_code, detail, headers)


class EmptyRequestBody(HTTPException):
    def __init__(
        self,
        status_code: int = RequestBody.empty.status_code,
        detail: str = RequestBody.empty.msg,
        headers: Mapping[str, str] = None,
    ):
        super().__init__(status_code, detail, headers)
